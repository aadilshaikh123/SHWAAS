"""
Test WAQI API integration
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from agents.waqi_collector import WAQICollector

print("="*70)
print("TESTING WAQI API INTEGRATION")
print("="*70)

# Get token from environment
token = os.getenv("WAQI_API_KEY") or os.getenv("WAQI_TOKEN")

if not token:
    print("\n❌ No WAQI token found in environment")
    print("Please set WAQI_API_KEY or WAQI_TOKEN in .env file")
    sys.exit(1)

print(f"\n✓ Token found: {token[:10]}...")

# Initialize collector
collector = WAQICollector(token)

# Test cities
test_cities = [
    ("Delhi", 28.6139, 77.2090),
    ("Mumbai", 19.0760, 72.8777),
    ("Pune", 18.5204, 73.8567),
    ("Beijing", 39.9042, 116.4074),
]

print("\n" + "="*70)
print("TESTING CITY LOOKUPS")
print("="*70)

for city_name, lat, lon in test_cities:
    print(f"\n{city_name}:")
    print("-" * 40)
    
    # Try by city name
    data = collector.fetch_by_city(city_name.lower())
    
    if data:
        print(f"  ✓ Data retrieved")
        print(f"  AQI: {data.get('aqi')}")
        print(f"  PM2.5: {data.get('pm25')} µg/m³")
        print(f"  PM10: {data.get('pm10')} µg/m³")
        print(f"  Dominant: {data.get('dominant_pollutant')}")
        print(f"  City: {data.get('city_name')}")
        print(f"  Temp: {data.get('temp')}°C")
        print(f"  Humidity: {data.get('humidity')}%")
        
        if data.get('forecast'):
            forecast = data['forecast']
            if forecast.get('pm25'):
                tomorrow = forecast['pm25'][0] if len(forecast['pm25']) > 0 else None
                if tomorrow:
                    print(f"  Tomorrow PM2.5: {tomorrow.get('avg')} µg/m³")
    else:
        print(f"  ❌ Failed to retrieve data")
        
        # Try by coordinates
        print(f"  Trying coordinates ({lat}, {lon})...")
        data = collector.fetch_by_coordinates(lat, lon)
        
        if data:
            print(f"  ✓ Data retrieved via coordinates")
            print(f"  AQI: {data.get('aqi')}")
            print(f"  City: {data.get('city_name')}")
        else:
            print(f"  ❌ Coordinates also failed")

print("\n" + "="*70)
print("TESTING IP-BASED LOCATION")
print("="*70)

data = collector.fetch_here()
if data:
    print(f"\n✓ Current location data:")
    print(f"  AQI: {data.get('aqi')}")
    print(f"  City: {data.get('city_name')}")
    print(f"  PM2.5: {data.get('pm25')} µg/m³")
else:
    print("\n❌ IP-based location failed")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nIf you see AQI data above, WAQI integration is working!")
print("The backend will now use WAQI as the primary data source.")
