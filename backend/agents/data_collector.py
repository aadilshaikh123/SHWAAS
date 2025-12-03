"""
DataCollector Agent - Fetches weather and AQI data
Primary source: WAQI (World Air Quality Index) ONLY
Fallback: Tavily search for AQI information
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.agents.waqi_collector import fetch_waqi_data


def fetch_weather_data_multi_day(lat: float, lon: float, city: Optional[str] = None) -> Dict:
    """
    Fetch weather and air quality data.
    Primary source: WAQI API ONLY
    Fallback: Tavily search for AQI information
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        city: City name for WAQI lookup
    
    Returns:
        Dict with keys: today (dict), tomorrow (dict)
    """
    # Get WAQI token from environment
    waqi_token = os.getenv("WAQI_API_KEY") or os.getenv("WAQI_TOKEN")
    
    if not waqi_token:
        raise Exception("WAQI_API_KEY not found in environment. This is required.")
    
    # Fetch from WAQI
    waqi_data = fetch_waqi_data(lat, lon, waqi_token, city)
    
    if not waqi_data:
        # WAQI failed - use Tavily as fallback
        print("⚠ WAQI failed, using Tavily fallback")
        return fetch_data_via_tavily(city or f"{lat},{lon}")
    
    # Convert WAQI data to standard format
    today_data = _convert_waqi_to_standard(waqi_data)
    print("✓ Using WAQI real-time data")
    
    # For tomorrow, use WAQI forecast if available, otherwise estimate
    tomorrow_data = _extract_waqi_forecast(waqi_data, today_data)
    
    return {
        "today": today_data,
        "tomorrow": tomorrow_data,
        "source": "WAQI",
        "timestamp": datetime.now().isoformat()
    }


def _extract_waqi_forecast(waqi_data: Dict, today_data: Dict) -> Dict:
    """
    Extract tomorrow's forecast from WAQI data or estimate from today.
    WAQI provides real-time data, not forecasts. We estimate tomorrow based on today.
    
    Args:
        waqi_data: Raw WAQI response
        today_data: Today's standardized data
    
    Returns:
        Tomorrow's estimated forecast dict
    """
    forecast = waqi_data.get("forecast", {})
    
    # Try to get tomorrow's PM2.5 from forecast (if available)
    pm25_forecast = forecast.get("pm25", [])
    pm10_forecast = forecast.get("pm10", [])
    
    # Start with today's data as baseline
    tomorrow = today_data.copy()
    
    if pm25_forecast and len(pm25_forecast) > 0:
        # Use first forecast day (tomorrow) if available
        tomorrow_pm25 = pm25_forecast[0].get("avg", today_data.get("pm25", 50))
        tomorrow["pm25"] = tomorrow_pm25
        tomorrow["source"] = "WAQI Forecast"
    else:
        # WAQI doesn't provide forecast - estimate based on today
        # Apply slight reduction (optimistic estimate)
        pm25_today = today_data.get("pm25", 50)
        tomorrow["pm25"] = pm25_today * 0.95  # 5% reduction estimate
        tomorrow["source"] = "Estimated from current"
    
    if pm10_forecast and len(pm10_forecast) > 0:
        tomorrow_pm10 = pm10_forecast[0].get("avg", today_data.get("pm10", 80))
        tomorrow["pm10"] = tomorrow_pm10
    else:
        pm10_today = today_data.get("pm10", 80)
        tomorrow["pm10"] = pm10_today * 0.95
    
    # Other pollutants: estimate with slight variation
    for pollutant in ["o3", "no2", "so2", "co"]:
        if pollutant in today_data and today_data[pollutant] is not None:
            tomorrow[pollutant] = today_data[pollutant] * 0.97
    
    return tomorrow


def fetch_data_via_tavily(location: str) -> Dict:
    """
    Fallback: Use Tavily to search for AQI information.
    
    Args:
        location: City name or coordinates
    
    Returns:
        Dict with estimated data
    """
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        raise Exception("Both WAQI and Tavily failed. Cannot fetch data.")
    
    try:
        # Search for current AQI
        from backend.agents.search_agent import SearchAgent
        search_agent = SearchAgent(tavily_key)
        
        query = f"current air quality index AQI {location} today PM2.5 PM10 pollutants"
        results = search_agent.search(query)
        
        # Parse results to extract AQI (basic implementation)
        estimated_aqi = 100  # Default moderate
        estimated_pm25 = 60
        estimated_pm10 = 80
        
        # Try to extract AQI from search results
        if results and "summary" in results:
            summary = results["summary"].lower()
            # Look for AQI numbers in summary
            import re
            aqi_match = re.search(r'aqi[:\s]+(\d+)', summary)
            if aqi_match:
                estimated_aqi = int(aqi_match.group(1))
                estimated_pm25 = estimated_aqi * 0.6  # Rough estimate
            
            pm25_match = re.search(r'pm2\.5[:\s]+(\d+)', summary)
            if pm25_match:
                estimated_pm25 = float(pm25_match.group(1))
            
            pm10_match = re.search(r'pm10[:\s]+(\d+)', summary)
            if pm10_match:
                estimated_pm10 = float(pm10_match.group(1))
        
        # Create basic data structure
        today_data = {
            "aqi": estimated_aqi,
            "pm25": estimated_pm25,
            "pm10": estimated_pm10,
            "o3": None,
            "no2": None,
            "so2": None,
            "co": None,
            "temp": None,
            "humidity": None,
            "wind": None,
            "pressure": None,
            "dominant_pollutant": "pm25",
            "city_name": location,
            "timestamp": datetime.now().isoformat(),
            "source": "Tavily Fallback",
            "aqi_sources": ["Tavily Search"]
        }
        
        tomorrow_data = today_data.copy()
        tomorrow_data["source"] = "Estimated"
        
        return {
            "today": today_data,
            "tomorrow": tomorrow_data,
            "source": "Tavily",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Tavily fallback failed: {e}")
        raise Exception("All data sources failed")


def _convert_waqi_to_standard(waqi_data: Dict) -> Dict:
    """
    Convert WAQI format to standard format
    
    Args:
        waqi_data: Data from WAQI API
    
    Returns:
        Standardized dict
    """
    return {
        "temp": waqi_data.get("temp"),
        "humidity": waqi_data.get("humidity"),
        "wind": waqi_data.get("wind"),
        "pressure": waqi_data.get("pressure"),
        "pm25": waqi_data.get("pm25"),
        "pm10": waqi_data.get("pm10"),
        "o3": waqi_data.get("o3"),
        "no2": waqi_data.get("no2"),
        "so2": waqi_data.get("so2"),
        "co": waqi_data.get("co"),
        "aqi": waqi_data.get("aqi"),
        "dominant_pollutant": waqi_data.get("dominant_pollutant"),
        "city_name": waqi_data.get("city_name"),
        "timestamp": waqi_data.get("timestamp"),
        "source": "WAQI",
        "aqi_sources": ["WAQI"]
    }


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
    Uses WAQI API ONLY with Tavily fallback.
    """
    
    def __init__(self):
        """Initialize the DataCollector agent."""
        pass
    
    def collect_data_multi_day(self, city: str, lat: float, lon: float) -> Dict:
        """
        Collect weather data for today and tomorrow with caching fallback.
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with keys: today, tomorrow (each containing weather data)
        """
        try:
            # Try to fetch fresh data from API
            data = fetch_weather_data_multi_day(lat, lon, city)
            
            # Save to cache on success
            save_to_cache(city, data)
            
            return data
            
        except Exception as e:
            print(f"API fetch failed: {e}. Attempting cache fallback...")
            
            # Fallback to cached data
            cached = get_cached_data(city)
            
            if cached:
                result = cached.get("data", {})
                result["source"] = "cache_stale" if cached.get("is_stale") else "cache"
                return result
            else:
                raise Exception(f"No data available for {city}. API failed and no cache found.")
