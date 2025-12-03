"""
WAQI (World Air Quality Index) Data Collector
Primary data source for real-time AQI data
"""
import requests
from typing import Dict, Optional
from datetime import datetime


class WAQICollector:
    """Collects AQI data from WAQI API"""
    
    def __init__(self, api_token: str):
        """
        Initialize WAQI collector
        
        Args:
            api_token: WAQI API token
        """
        self.api_token = api_token
        self.base_url = "https://api.waqi.info"
    
    def fetch_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch AQI data by coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with AQI data or None if failed
        """
        try:
            url = f"{self.base_url}/feed/geo:{lat};{lon}/"
            params = {"token": self.api_token}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"WAQI API error: {data.get('data', 'Unknown error')}")
                return None
            
            return self._parse_waqi_response(data.get("data", {}))
            
        except Exception as e:
            print(f"WAQI API failed: {e}")
            return None
    
    def fetch_by_city(self, city: str) -> Optional[Dict]:
        """
        Fetch AQI data by city name
        
        Args:
            city: City name (e.g., "delhi", "mumbai", "beijing")
        
        Returns:
            Dict with AQI data or None if failed
        """
        try:
            url = f"{self.base_url}/feed/{city}/"
            params = {"token": self.api_token}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"WAQI API error for {city}: {data.get('data', 'Unknown error')}")
                return None
            
            return self._parse_waqi_response(data.get("data", {}))
            
        except Exception as e:
            print(f"WAQI API failed for {city}: {e}")
            return None
    
    def fetch_here(self) -> Optional[Dict]:
        """
        Fetch AQI data for current location (IP-based)
        
        Returns:
            Dict with AQI data or None if failed
        """
        try:
            url = f"{self.base_url}/feed/here/"
            params = {"token": self.api_token}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return None
            
            return self._parse_waqi_response(data.get("data", {}))
            
        except Exception as e:
            print(f"WAQI 'here' API failed: {e}")
            return None
    
    def _parse_waqi_response(self, data: Dict) -> Dict:
        """
        Parse WAQI API response into standardized format
        
        Args:
            data: WAQI API response data
        
        Returns:
            Standardized dict with pollutant data
        """
        iaqi = data.get("iaqi", {})
        
        # Extract pollutants
        result = {
            "aqi": data.get("aqi", 0),
            "pm25": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "temp": iaqi.get("t", {}).get("v"),
            "humidity": iaqi.get("h", {}).get("v"),
            "pressure": iaqi.get("p", {}).get("v"),
            "wind": iaqi.get("w", {}).get("v"),
            "dominant_pollutant": data.get("dominentpol", "unknown"),
            "city_name": data.get("city", {}).get("name", "Unknown"),
            "city_url": data.get("city", {}).get("url", ""),
            "station_id": data.get("idx"),
            "timestamp": data.get("time", {}).get("iso"),
            "source": "WAQI",
            "aqi_sources": ["WAQI"]
        }
        
        # Get forecast if available
        forecast = data.get("forecast", {}).get("daily", {})
        if forecast:
            result["forecast"] = {
                "pm25": forecast.get("pm25", []),
                "pm10": forecast.get("pm10", []),
                "o3": forecast.get("o3", []),
                "uvi": forecast.get("uvi", [])
            }
        
        # Remove None values
        result = {k: v for k, v in result.items() if v is not None}
        
        return result
    
    def get_city_coordinates(self, data: Dict) -> Optional[tuple]:
        """
        Extract coordinates from WAQI response
        
        Args:
            data: Parsed WAQI data
        
        Returns:
            Tuple of (lat, lon) or None
        """
        try:
            # WAQI doesn't return coordinates in standard response
            # Would need to use search API or maintain city database
            return None
        except:
            return None


def fetch_waqi_data(lat: float, lon: float, api_token: Optional[str] = None, city: Optional[str] = None) -> Optional[Dict]:
    """
    Convenience function to fetch WAQI data
    
    Args:
        lat: Latitude
        lon: Longitude
        api_token: WAQI API token
        city: Optional city name for direct lookup
    
    Returns:
        Dict with AQI data or None if failed
    """
    if not api_token:
        return None
    
    collector = WAQICollector(api_token)
    
    # Try city name first if provided
    if city:
        result = collector.fetch_by_city(city.lower())
        if result:
            return result
    
    # Fall back to coordinates
    return collector.fetch_by_coordinates(lat, lon)


# Example usage
if __name__ == "__main__":
    # Test with demo token
    token = "demo"
    collector = WAQICollector(token)
    
    # Test Beijing
    print("Testing Beijing:")
    data = collector.fetch_by_city("beijing")
    if data:
        print(f"  AQI: {data.get('aqi')}")
        print(f"  PM2.5: {data.get('pm25')}")
        print(f"  City: {data.get('city_name')}")
    
    # Test coordinates (Delhi)
    print("\nTesting Delhi coordinates:")
    data = collector.fetch_by_coordinates(28.6139, 77.2090)
    if data:
        print(f"  AQI: {data.get('aqi')}")
        print(f"  PM2.5: {data.get('pm25')}")
        print(f"  City: {data.get('city_name')}")
