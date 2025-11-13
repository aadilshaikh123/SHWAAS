"""
OpenAQ Agent - Fetches real air quality sensor data from OpenAQ API
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenAQAgent:
    """
    Agent responsible for fetching real air quality data from OpenAQ sensors.
    Provides actual measurements instead of estimates for better accuracy.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAQ agent.
        
        Args:
            api_key: OpenAQ API key (optional, but recommended for higher rate limits)
        """
        self.api_key = api_key
        self.base_url = "https://api.openaq.org/v2"
        self.headers = {}
        
        if api_key:
            self.headers["X-API-Key"] = api_key
            logger.info("OpenAQ agent initialized with API key")
        else:
            logger.warning("OpenAQ agent initialized without API key (lower rate limits)")
    
    def get_latest_measurements(self, lat: float, lon: float, radius_km: int = 25) -> Optional[Dict]:
        """
        Get latest air quality measurements near a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers (default: 25km)
        
        Returns:
            Dict with pollutant measurements or None if no data available
        """
        try:
            # OpenAQ v2 API endpoint for latest measurements
            url = f"{self.base_url}/latest"
            
            params = {
                "coordinates": f"{lat},{lon}",
                "radius": radius_km * 1000,  # Convert to meters
                "limit": 100,  # Get multiple stations
                "order_by": "distance"
            }
            
            logger.info(f"Fetching OpenAQ data for ({lat}, {lon}) within {radius_km}km")
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.warning(f"No OpenAQ sensors found within {radius_km}km of ({lat}, {lon})")
                return None
            
            logger.info(f"Found {len(results)} OpenAQ sensors")
            
            # Aggregate measurements from multiple sensors
            return self._aggregate_measurements(results)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAQ API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing OpenAQ data: {e}")
            return None
    
    def _aggregate_measurements(self, results: List[Dict]) -> Dict:
        """
        Aggregate measurements from multiple sensors.
        
        Args:
            results: List of sensor results from OpenAQ API
        
        Returns:
            Dict with aggregated pollutant values
        """
        # Collect all measurements by parameter
        measurements = {
            "pm25": [],
            "pm10": [],
            "o3": [],
            "no2": [],
            "so2": [],
            "co": []
        }
        
        parameter_map = {
            "pm25": "pm25",
            "pm2.5": "pm25",
            "pm10": "pm10",
            "o3": "o3",
            "no2": "no2",
            "so2": "so2",
            "co": "co"
        }
        
        for result in results:
            measurements_list = result.get("measurements", [])
            
            for measurement in measurements_list:
                parameter = measurement.get("parameter", "").lower()
                value = measurement.get("value")
                unit = measurement.get("unit", "")
                
                # Map parameter name
                param_key = parameter_map.get(parameter)
                
                if param_key and value is not None:
                    # Convert units if needed
                    converted_value = self._convert_units(value, unit, param_key)
                    if converted_value is not None:
                        measurements[param_key].append(converted_value)
        
        # Calculate averages
        aggregated = {}
        for param, values in measurements.items():
            if values:
                avg_value = sum(values) / len(values)
                aggregated[param] = round(avg_value, 2)
                logger.info(f"OpenAQ {param.upper()}: {avg_value:.2f} µg/m³ (from {len(values)} sensors)")
        
        if not aggregated:
            logger.warning("No valid measurements found in OpenAQ data")
            return None
        
        aggregated["source"] = "OpenAQ"
        aggregated["sensor_count"] = len(results)
        
        return aggregated
    
    def _convert_units(self, value: float, unit: str, parameter: str) -> Optional[float]:
        """
        Convert measurement units to µg/m³.
        
        Args:
            value: Measurement value
            unit: Current unit
            parameter: Pollutant parameter
        
        Returns:
            Converted value in µg/m³ or None if conversion not possible
        """
        unit = unit.lower().strip()
        
        # Already in µg/m³
        if unit in ["µg/m³", "ug/m3", "μg/m³"]:
            return value
        
        # Convert ppm to µg/m³ (approximate, depends on molecular weight)
        if unit == "ppm":
            # Molecular weights (g/mol)
            mw = {
                "co": 28.01,
                "no2": 46.01,
                "so2": 64.07,
                "o3": 48.00
            }
            
            if parameter in mw:
                # ppm to µg/m³: (ppm * MW * 1000) / 24.45
                return (value * mw[parameter] * 1000) / 24.45
        
        # Convert ppb to µg/m³
        if unit == "ppb":
            mw = {
                "co": 28.01,
                "no2": 46.01,
                "so2": 64.07,
                "o3": 48.00
            }
            
            if parameter in mw:
                # ppb to µg/m³: (ppb * MW) / 24.45
                return (value * mw[parameter]) / 24.45
        
        logger.warning(f"Unknown unit '{unit}' for {parameter}, using value as-is")
        return value
    
    def get_sensor_info(self, lat: float, lon: float, radius_km: int = 25) -> List[Dict]:
        """
        Get information about nearby sensors.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
        
        Returns:
            List of sensor information dicts
        """
        try:
            url = f"{self.base_url}/locations"
            
            params = {
                "coordinates": f"{lat},{lon}",
                "radius": radius_km * 1000,
                "limit": 10,
                "order_by": "distance"
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            sensors = []
            for result in results:
                sensors.append({
                    "name": result.get("name"),
                    "city": result.get("city"),
                    "country": result.get("country"),
                    "distance_km": result.get("distance", 0) / 1000,
                    "parameters": [p.get("parameter") for p in result.get("parameters", [])]
                })
            
            return sensors
            
        except Exception as e:
            logger.error(f"Error fetching sensor info: {e}")
            return []
