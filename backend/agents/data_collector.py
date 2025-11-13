"""
DataCollector Agent - Fetches weather and AQI data from Open-Meteo API
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from zoneinfo import ZoneInfo


def validate_weather_data(data: Dict) -> Dict:
    """
    Validate weather data against realistic ranges.
    
    Args:
        data: Weather data dict with temp, humidity, wind, pm25
    
    Returns:
        Validated data dict
    
    Raises:
        ValueError: If data is outside realistic ranges
    """
    # Validate temperature: -50°C to 60°C
    if data.get("temp") is not None:
        if not (-50 <= data["temp"] <= 60):
            raise ValueError(f"Temperature {data['temp']}°C is outside realistic range (-50°C to 60°C)")
    
    # Validate humidity: 0% to 100%
    if data.get("humidity") is not None:
        if not (0 <= data["humidity"] <= 100):
            raise ValueError(f"Humidity {data['humidity']}% is outside valid range (0% to 100%)")
    
    # Validate wind speed: >= 0 km/h
    if data.get("wind") is not None:
        if data["wind"] < 0:
            raise ValueError(f"Wind speed {data['wind']} km/h cannot be negative")
    
    # Validate PM2.5: 0 to 1000 µg/m³
    if data.get("pm25") is not None:
        if not (0 <= data["pm25"] <= 1000):
            raise ValueError(f"PM2.5 {data['pm25']} µg/m³ is outside realistic range (0 to 1000 µg/m³)")
    
    return data


def fetch_weather_data_multi_day(lat: float, lon: float) -> Dict:
    """
    Fetch weather data and air quality from Open-Meteo API for today and tomorrow.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Dict with keys: today (dict), tomorrow (dict)
    """
    # Today: Use current hour for more accurate current conditions
    today_data = fetch_weather_data_for_day(lat, lon, 0, use_current_time=True)
    
    # Tomorrow: Use noon (12 PM) for consistent forecast
    tomorrow_data = fetch_weather_data_for_day(lat, lon, 1, use_current_time=False)
    
    return {
        "today": today_data,
        "tomorrow": tomorrow_data
    }


def fetch_weather_data(lat: float, lon: float) -> Dict:
    """
    Fetch weather data and air quality from Open-Meteo API for tomorrow's forecast.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Dict with keys: temp, humidity, wind, pm25, pm10, o3, no2, so2, co, aqi_sources
    """
    return fetch_weather_data_for_day(lat, lon, 1)  # 1 = tomorrow


def fetch_weather_data_for_day(lat: float, lon: float, day_offset: int = 1, use_current_time: bool = False) -> Dict:
    """
    Fetch weather data and air quality from Open-Meteo API for a specific day.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        day_offset: 0 for today, 1 for tomorrow
        use_current_time: If True, use current hour instead of noon (for today's data)
    
    Returns:
        Dict with keys: temp, humidity, wind, pm25, pm10, o3, no2, so2, co, aqi_sources
    """
    try:
        # Open-Meteo Forecast API endpoint for weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        
        # Request parameters for weather forecast
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "forecast_days": 2,
            "timezone": "auto"
        }
        
        # Fetch weather data
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Try to fetch air quality data with multiple pollutants (optional, may fail)
        air_data = None
        pollutants_available = []
        try:
            air_quality_url = "https://air-quality.open-meteo.com/v1/air-quality"
            air_params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "pm2_5,pm10,ozone,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,us_aqi,european_aqi",
                "forecast_days": 2,
                "timezone": "auto"
            }
            air_response = requests.get(air_quality_url, params=air_params, timeout=5)
            if air_response.status_code == 200:
                air_data = air_response.json()
                pollutants_available.append("Open-Meteo Air Quality API")
            else:
                air_data = None
        except Exception as e:
            print(f"Air quality API unavailable, will use estimated values: {e}")
            air_data = None
        
        # Get timezone from API response
        timezone_str = weather_data.get("timezone")
        if not timezone_str:
            raise ValueError("Timezone information not available from API")
        
        # Parse timezone
        try:
            tz = ZoneInfo(timezone_str)
        except Exception as e:
            raise ValueError(f"Invalid timezone '{timezone_str}': {str(e)}")
        
        # Get current time in the location's timezone
        now_local = datetime.now(tz)
        
        # Calculate target time based on parameters
        if use_current_time and day_offset == 0:
            # For today, use current hour (more accurate current conditions)
            target_time = now_local
        else:
            # For tomorrow or when not using current time, use noon
            target_time = (now_local + timedelta(days=day_offset)).replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Parse the time array from weather API response
        weather_hourly = weather_data.get("hourly", {})
        time_array = weather_hourly.get("time", [])
        
        if not time_array:
            raise ValueError("No time data available from API")
        
        # Find the index for target time
        # Time array contains ISO format strings like "2024-01-15T12:00"
        target_time_str = target_time.strftime("%Y-%m-%dT%H:%M")
        
        idx = None
        for i, time_str in enumerate(time_array):
            if time_str.startswith(target_time_str[:13]):  # Match up to hour
                idx = i
                break
        
        if idx is None:
            # Fallback: calculate index based on hours difference
            first_time = datetime.fromisoformat(time_array[0]).replace(tzinfo=tz)
            hours_diff = int((target_time - first_time).total_seconds() / 3600)
            idx = max(0, min(hours_diff, len(time_array) - 1))
        
        # Get air quality data at the same time index if available
        pm25_value = None
        pm10_value = None
        o3_value = None
        no2_value = None
        so2_value = None
        co_value = None
        us_aqi_value = None
        eu_aqi_value = None
        
        if air_data:
            air_hourly = air_data.get("hourly", {})
            
            # Extract all available pollutants
            pm25_array = air_hourly.get("pm2_5", [])
            pm10_array = air_hourly.get("pm10", [])
            o3_array = air_hourly.get("ozone", [])
            no2_array = air_hourly.get("nitrogen_dioxide", [])
            so2_array = air_hourly.get("sulphur_dioxide", [])
            co_array = air_hourly.get("carbon_monoxide", [])
            us_aqi_array = air_hourly.get("us_aqi", [])
            eu_aqi_array = air_hourly.get("european_aqi", [])
            
            if pm25_array and idx < len(pm25_array):
                pm25_value = pm25_array[idx]
            if pm10_array and idx < len(pm10_array):
                pm10_value = pm10_array[idx]
            if o3_array and idx < len(o3_array):
                o3_value = o3_array[idx]
            if no2_array and idx < len(no2_array):
                no2_value = no2_array[idx]
            if so2_array and idx < len(so2_array):
                so2_value = so2_array[idx]
            if co_array and idx < len(co_array):
                co_value = co_array[idx]
            if us_aqi_array and idx < len(us_aqi_array):
                us_aqi_value = us_aqi_array[idx]
            if eu_aqi_array and idx < len(eu_aqi_array):
                eu_aqi_value = eu_aqi_array[idx]
        
        # If pollutants not available, estimate based on location, weather, and time
        # Note: These are estimations and may not reflect real-time conditions
        if pm25_value is None:
            humidity = weather_hourly.get("relative_humidity_2m", [None])[idx]
            wind = weather_hourly.get("wind_speed_10m", [None])[idx]
            temp = weather_hourly.get("temperature_2m", [None])[idx]
            
            # Get hour of day for time-based adjustments
            target_hour = target_time.hour
            
            # Estimate base PM2.5 based on geographic location
            # Indian subcontinent and South Asia typically have higher pollution
            # Using latitude/longitude as rough indicators
            if 8 <= lat <= 35 and 68 <= lon <= 97:  # India region
                # Indian cities have significantly higher pollution
                # Winter months (Nov-Feb) are worse due to crop burning, fireworks, and temperature inversion
                current_month = datetime.now().month
                if current_month in [11, 12, 1, 2]:  # Winter months
                    base_pm25 = 120.0  # Very high baseline in winter
                elif current_month in [3, 4, 10]:  # Transition months
                    base_pm25 = 95.0
                else:  # Summer/Monsoon (May-Sep)
                    base_pm25 = 75.0  # Lower due to rain and wind
            elif 20 <= lat <= 40 and 100 <= lon <= 125:  # East Asia
                base_pm25 = 80.0
            elif 30 <= lat <= 50 and -10 <= lon <= 40:  # Europe
                base_pm25 = 25.0
            elif 25 <= lat <= 50 and -125 <= lon <= -65:  # North America
                base_pm25 = 35.0
            else:
                base_pm25 = 50.0  # Global average
            
            # Time-of-day adjustment (pollution varies throughout the day)
            time_factor = 0
            if 6 <= target_hour <= 9:  # Morning rush hour
                time_factor = 0.25  # 25% increase
            elif 17 <= target_hour <= 20:  # Evening rush hour
                time_factor = 0.30  # 30% increase (worse than morning)
            elif 22 <= target_hour or target_hour <= 5:  # Night/early morning
                time_factor = -0.15  # 15% decrease (less traffic)
            else:  # Midday
                time_factor = 0.05  # Slight increase
            
            base_pm25 = base_pm25 * (1 + time_factor)
            
            if humidity is not None and wind is not None and temp is not None:
                # Weather-based adjustments
                # Higher humidity increases PM2.5 (moisture traps particles)
                humidity_factor = (humidity - 50) / 50  # -1.0 to +1.0
                # Higher wind decreases PM2.5 (disperses particles)
                wind_factor = (wind - 5) / 10  # Adjusted for typical wind speeds
                # Temperature inversion can trap pollutants
                temp_factor = 0
                if temp < 15:  # Cold weather can trap pollutants
                    temp_factor = (15 - temp) / 15  # 0 to 1
                
                # Apply factors with realistic weights
                pm25_value = base_pm25 + (humidity_factor * 25) - (wind_factor * 20) + (temp_factor * 15)
                
                # Add some variability (±20%) to simulate real-world fluctuations
                import random
                random.seed(int(lat * 1000 + lon * 1000))  # Deterministic based on location
                variability = random.uniform(0.85, 1.15)
                pm25_value = pm25_value * variability
                
                # Clamp to realistic ranges
                pm25_value = max(10.0, min(pm25_value, 250.0))
            else:
                pm25_value = base_pm25
        
        # Estimate other pollutants if not available
        if pm10_value is None and pm25_value is not None:
            # PM10 is typically 1.5-2x PM2.5
            pm10_value = pm25_value * 1.7
        
        if o3_value is None:
            # Ozone estimation: higher in summer, lower in winter, increases with temperature
            temp_val = weather_hourly.get("temperature_2m", [None])[idx]
            if temp_val is not None:
                # Base ozone around 50-80 µg/m³, increases with temperature
                o3_value = 60 + (temp_val - 20) * 2
                o3_value = max(20, min(o3_value, 180))
            else:
                o3_value = 60.0
        
        if no2_value is None:
            # NO2 estimation: higher in urban areas, correlates with PM2.5
            if pm25_value is not None:
                no2_value = pm25_value * 0.4  # Rough correlation
            else:
                no2_value = 30.0
        
        if so2_value is None:
            # SO2 estimation: typically lower than NO2
            if no2_value is not None:
                so2_value = no2_value * 0.3
            else:
                so2_value = 10.0
        
        if co_value is None:
            # CO estimation: correlates with traffic and combustion
            if pm25_value is not None:
                co_value = pm25_value * 15  # CO is measured in µg/m³, typically much higher
            else:
                co_value = 500.0
        
        # Determine AQI sources
        aqi_sources = []
        if us_aqi_value is not None:
            aqi_sources.append("US EPA AQI (Open-Meteo)")
        if eu_aqi_value is not None:
            aqi_sources.append("European AQI (Open-Meteo)")
        if not aqi_sources:
            aqi_sources.append("Estimated from pollutants")
        
        result = {
            "temp": weather_hourly["temperature_2m"][idx] if weather_hourly.get("temperature_2m") else None,
            "humidity": weather_hourly["relative_humidity_2m"][idx] if weather_hourly.get("relative_humidity_2m") else None,
            "wind": weather_hourly["wind_speed_10m"][idx] if weather_hourly.get("wind_speed_10m") else None,
            "pm25": round(pm25_value, 2) if pm25_value is not None else 30.0,
            "pm10": round(pm10_value, 2) if pm10_value is not None else None,
            "o3": round(o3_value, 2) if o3_value is not None else None,
            "no2": round(no2_value, 2) if no2_value is not None else None,
            "so2": round(so2_value, 2) if so2_value is not None else None,
            "co": round(co_value, 2) if co_value is not None else None,
            "us_aqi": int(us_aqi_value) if us_aqi_value is not None else None,
            "eu_aqi": int(eu_aqi_value) if eu_aqi_value is not None else None,
            "aqi_sources": aqi_sources,
            "forecast_time": target_time.strftime("%I:%M %p"),  # e.g., "06:00 PM"
            "forecast_hour": target_time.hour,  # e.g., 18
            "forecast_date": target_time.strftime("%Y-%m-%d"),  # e.g., "2024-01-15"
        }
        
        # Validate data before returning
        result = validate_weather_data(result)
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Failed to parse weather data: {str(e)}")


def get_cached_data(city: str) -> Optional[Dict]:
    """
    Retrieve cached weather data for a city.
    
    Args:
        city: City name
    
    Returns:
        Dict with cached data or None if not available
    """
    cache_dir = "backend/cache"
    cache_file = os.path.join(cache_dir, f"{city}_latest.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        # Check staleness (6-hour threshold)
        timestamp = datetime.fromisoformat(cached.get("timestamp", ""))
        age = datetime.now() - timestamp
        
        if age.total_seconds() > 6 * 3600:
            cached["is_stale"] = True
        else:
            cached["is_stale"] = False
        
        return cached
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error reading cache for {city}: {e}")
        return None


def save_to_cache(city: str, data: Dict) -> None:
    """
    Save weather data to cache.
    
    Args:
        city: City name
        data: Weather data dict
    """
    cache_dir = "backend/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{city}_latest.json")
    
    cache_data = {
        "city": city,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Error saving cache for {city}: {e}")


class DataCollectorAgent:
    """
    Agent responsible for collecting weather and AQI data.
    Uses Open-Meteo API with caching fallback for offline resilience.
    Optionally uses OpenAQ for real sensor data.
    Refactored to plain Python class without Phidata wrapper.
    """
    
    def __init__(self, openaq_api_key: Optional[str] = None):
        """
        Initialize the DataCollector agent.
        
        Args:
            openaq_api_key: Optional OpenAQ API key for real sensor data
        """
        self.openaq_agent = None
        
        if openaq_api_key:
            try:
                from backend.agents.openaq_agent import OpenAQAgent
                self.openaq_agent = OpenAQAgent(openaq_api_key)
                print("OpenAQ integration enabled - will use real sensor data when available")
            except Exception as e:
                print(f"Failed to initialize OpenAQ agent: {e}")
                self.openaq_agent = None
    
    def collect_data(self, city: str, lat: float, lon: float) -> Dict:
        """
        Collect weather data for a city with caching fallback.
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with weather data: {temp, humidity, wind, pm25, source, timestamp}
        """
        try:
            # Try to fetch fresh data from API
            data = fetch_weather_data(lat, lon)
            
            # Save to cache on success
            save_to_cache(city, data)
            
            data["source"] = "api"
            data["timestamp"] = datetime.now().isoformat()
            return data
            
        except Exception as e:
            print(f"API fetch failed: {e}. Attempting cache fallback...")
            
            # Fallback to cached data
            cached = get_cached_data(city)
            
            if cached:
                result = cached.get("data", {})
                result["source"] = "cache_stale" if cached.get("is_stale") else "cache"
                result["timestamp"] = cached.get("timestamp", datetime.now().isoformat())
                return result
            else:
                raise Exception(f"No data available for {city}. API failed and no cache found.")
    
    def collect_data_multi_day(self, city: str, lat: float, lon: float) -> Dict:
        """
        Collect weather data for today and tomorrow with caching fallback.
        Optionally enhances with real OpenAQ sensor data.
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with keys: today, tomorrow (each containing weather data)
        """
        try:
            # Try to fetch fresh data from API
            data = fetch_weather_data_multi_day(lat, lon)
            
            # Try to enhance with OpenAQ real sensor data
            if self.openaq_agent:
                try:
                    openaq_data = self.openaq_agent.get_latest_measurements(lat, lon, radius_km=25)
                    
                    if openaq_data:
                        print(f"✓ OpenAQ data available - using real sensor measurements")
                        
                        # Get sensor information for display
                        sensor_info = self.openaq_agent.get_sensor_info(lat, lon, radius_km=25)
                        data["openaq_sensors"] = sensor_info[:5]  # Top 5 nearest sensors
                        
                        # Update today's data with real measurements
                        if data.get("today"):
                            data["today"] = self._merge_openaq_data(data["today"], openaq_data)
                            data["today"]["has_real_data"] = True
                            data["today"]["sensor_count"] = openaq_data.get("sensor_count", 0)
                        
                        # For tomorrow, use OpenAQ as baseline (more accurate than estimates)
                        if data.get("tomorrow"):
                            data["tomorrow"] = self._merge_openaq_data(data["tomorrow"], openaq_data, is_forecast=True)
                            data["tomorrow"]["sensor_count"] = openaq_data.get("sensor_count", 0)
                    else:
                        print("ℹ No OpenAQ sensors found nearby - using estimates")
                        data["openaq_sensors"] = []
                        
                except Exception as e:
                    print(f"OpenAQ enhancement failed: {e} - continuing with estimates")
                    data["openaq_sensors"] = []
            
            # Add metadata
            data["source"] = "api"
            data["timestamp"] = datetime.now().isoformat()
            return data
            
        except Exception as e:
            print(f"API fetch failed: {e}. Attempting single-day fallback...")
            
            # Fallback to single day (tomorrow only)
            tomorrow_data = self.collect_data(city, lat, lon)
            return {
                "today": None,
                "tomorrow": tomorrow_data,
                "source": tomorrow_data.get("source"),
                "timestamp": tomorrow_data.get("timestamp")
            }
    
    def _merge_openaq_data(self, forecast_data: Dict, openaq_data: Dict, is_forecast: bool = False) -> Dict:
        """
        Merge OpenAQ real sensor data with forecast data.
        
        Args:
            forecast_data: Weather forecast data
            openaq_data: Real sensor data from OpenAQ
            is_forecast: If True, adjust values slightly for tomorrow
        
        Returns:
            Merged data dict
        """
        # Use OpenAQ data for pollutants (more accurate)
        if "pm25" in openaq_data:
            # For tomorrow, add slight variation based on forecast trends
            if is_forecast:
                # Adjust based on weather conditions
                temp_factor = 1.0
                wind = forecast_data.get("wind", 10)
                humidity = forecast_data.get("humidity", 50)
                
                # Higher wind = lower pollution
                if wind > 15:
                    temp_factor *= 0.95
                elif wind < 5:
                    temp_factor *= 1.05
                
                # Higher humidity = higher pollution (traps particles)
                if humidity > 70:
                    temp_factor *= 1.03
                
                forecast_data["pm25"] = round(openaq_data["pm25"] * temp_factor, 2)
            else:
                forecast_data["pm25"] = openaq_data["pm25"]
        
        if "pm10" in openaq_data:
            factor = 1.0 if not is_forecast else (1.0 + (forecast_data.get("wind", 10) - 10) * 0.01)
            forecast_data["pm10"] = round(openaq_data["pm10"] * factor, 2)
        
        if "o3" in openaq_data:
            forecast_data["o3"] = round(openaq_data["o3"], 2)
        
        if "no2" in openaq_data:
            forecast_data["no2"] = round(openaq_data["no2"], 2)
        
        if "so2" in openaq_data:
            forecast_data["so2"] = round(openaq_data["so2"], 2)
        
        if "co" in openaq_data:
            forecast_data["co"] = round(openaq_data["co"], 2)
        
        # Add source information
        forecast_data["aqi_sources"] = [f"OpenAQ ({openaq_data.get('sensor_count', 0)} sensors)"]
        
        return forecast_data
