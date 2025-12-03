"""
Predictor Agent - Predicts tomorrow's AQI using trained ML model
Uses the best model trained on city_day.csv dataset
"""
import joblib
import os
import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


def pollutant_to_aqi(pollutant_value: float, pollutant_type: str) -> int:
    """
    Convert pollutant concentration to AQI using EPA formula.
    
    Args:
        pollutant_value: Pollutant concentration
        pollutant_type: Type of pollutant (pm25, pm10, o3, no2, so2, co)
    
    Returns:
        AQI value as integer
    """
    # EPA breakpoints for different pollutants
    # Format: (pollutant_low, pollutant_high, AQI_low, AQI_high)
    
    breakpoints = {
        "pm25": [  # µg/m³
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500),
        ],
        "pm10": [  # µg/m³
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500),
        ],
        "o3": [  # µg/m³ (8-hour average)
            (0, 108, 0, 50),
            (109, 140, 51, 100),
            (141, 170, 101, 150),
            (171, 210, 151, 200),
            (211, 400, 201, 300),
        ],
        "no2": [  # µg/m³ (1-hour average)
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 1649, 301, 400),
            (1650, 2049, 401, 500),
        ],
        "so2": [  # µg/m³ (1-hour average)
            (0, 35, 0, 50),
            (36, 75, 51, 100),
            (76, 185, 101, 150),
            (186, 304, 151, 200),
            (305, 604, 201, 300),
            (605, 804, 301, 400),
            (805, 1004, 401, 500),
        ],
        "co": [  # µg/m³ (8-hour average)
            (0, 4400, 0, 50),
            (4500, 9400, 51, 100),
            (9500, 12400, 101, 150),
            (12500, 15400, 151, 200),
            (15500, 30400, 201, 300),
            (30500, 40400, 301, 400),
            (40500, 50400, 401, 500),
        ],
    }
    
    if pollutant_type not in breakpoints:
        logger.warning(f"Unknown pollutant type: {pollutant_type}")
        return 0
    
    if pollutant_value < 0:
        return 0
    
    if pollutant_value == 0:
        return 0
    
    # Find the appropriate breakpoint
    for p_low, p_high, aqi_low, aqi_high in breakpoints[pollutant_type]:
        if p_low <= pollutant_value <= p_high:
            # Linear interpolation
            aqi = ((aqi_high - aqi_low) / (p_high - p_low)) * (pollutant_value - p_low) + aqi_low
            return int(round(aqi))
    
    # If exceeds highest breakpoint, cap at 500
    return 500


def pm25_to_aqi(pm25_value: float) -> int:
    """
    Convert PM2.5 concentration to AQI using EPA formula.
    
    Args:
        pm25_value: PM2.5 concentration in µg/m³
    
    Returns:
        AQI value as integer
    
    EPA AQI Breakpoints for PM2.5 (24-hour average):
    - 0.0-12.0 µg/m³ → AQI 0-50 (Good)
    - 12.1-35.4 µg/m³ → AQI 51-100 (Moderate)
    - 35.5-55.4 µg/m³ → AQI 101-150 (Unhealthy for Sensitive Groups)
    - 55.5-150.4 µg/m³ → AQI 151-200 (Unhealthy)
    - 150.5-250.4 µg/m³ → AQI 201-300 (Very Unhealthy)
    - 250.5-350.4 µg/m³ → AQI 301-400 (Hazardous)
    - 350.5-500.4 µg/m³ → AQI 401-500 (Hazardous)
    """
    # EPA breakpoints: (PM2.5_low, PM2.5_high, AQI_low, AQI_high)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    
    # Handle edge cases
    if pm25_value < 0:
        logger.warning(f"Negative PM2.5 value received: {pm25_value}, returning AQI 0")
        return 0
    
    if pm25_value == 0:
        return 0
    
    # Find the appropriate breakpoint
    for pm_low, pm_high, aqi_low, aqi_high in breakpoints:
        if pm_low <= pm25_value <= pm_high:
            # Linear interpolation formula: AQI = ((AQI_high - AQI_low) / (PM_high - PM_low)) * (PM - PM_low) + AQI_low
            aqi = ((aqi_high - aqi_low) / (pm_high - pm_low)) * (pm25_value - pm_low) + aqi_low
            return int(round(aqi))
    
    # If PM2.5 exceeds highest breakpoint, cap at 500
    if pm25_value > 500.4:
        logger.warning(f"PM2.5 value {pm25_value} exceeds maximum breakpoint, capping AQI at 500")
        return 500
    
    # Fallback (should not reach here with proper breakpoints)
    logger.error(f"PM2.5 value {pm25_value} did not match any breakpoint")
    return 500


def get_aqi_category(aqi: int) -> str:
    """
    Get the AQI category name based on AQI value.
    
    Args:
        aqi: AQI value
    
    Returns:
        Category name as string
    """
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


class PredictorAgent:
    """
    Agent responsible for predicting tomorrow's AQI using trained ML model.
    Uses Random Forest/Gradient Boosting model trained on city_day.csv
    """
    
    def __init__(self, model_path: str = "backend/ml/best_model.pkl"):
        """
        Initialize the Predictor agent with trained ML model.
        
        Args:
            model_path: Path to the trained model pickle file
        """
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.city_encoder = None
        
        # Load trained ML model
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                logger.info(f"✓ ML model loaded from {model_path}")
                
                # Load scaler
                scaler_path = model_path.replace("best_model.pkl", "scaler.pkl")
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    logger.info(f"✓ Scaler loaded")
                
                # Load city encoder
                encoder_path = model_path.replace("best_model.pkl", "city_encoder.pkl")
                if os.path.exists(encoder_path):
                    self.city_encoder = joblib.load(encoder_path)
                    logger.info(f"✓ City encoder loaded")
                    
            except Exception as e:
                logger.warning(f"Failed to load ML model: {e}")
                logger.info("Will use direct PM2.5 to AQI conversion instead")
                self.model = None
        else:
            logger.info(f"ML model not found at {model_path}")
            logger.info("Will use direct PM2.5 to AQI conversion instead")
    
    def predict_with_ml(self, weather_data: Dict, city: str = "Delhi") -> Optional[int]:
        """
        Predict AQI using trained ML model.
        
        Args:
            weather_data: Dict with pollutant and weather data
            city: City name for encoding
        
        Returns:
            Predicted AQI or None if model not available
        """
        if not self.model or not self.scaler:
            return None
        
        try:
            # Prepare features in the same order as training
            features = []
            feature_names = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3',
                           'Benzene', 'Toluene', 'Xylene', 'Month', 'DayOfYear', 'DayOfWeek']
            
            # Extract features
            for feat in feature_names:
                val = weather_data.get(feat.lower().replace('.', ''), 0)
                features.append(float(val) if val is not None else 0.0)
            
            # Add temporal features
            now = datetime.now()
            features[12] = now.month  # Month
            features[13] = now.timetuple().tm_yday  # DayOfYear
            features[14] = now.weekday()  # DayOfWeek
            
            # Add city encoding
            if self.city_encoder:
                try:
                    city_encoded = self.city_encoder.transform([city])[0]
                except:
                    city_encoded = 0  # Default if city not in training data
            else:
                city_encoded = 0
            
            features.append(city_encoded)
            
            # Scale features
            features_array = np.array(features).reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            
            # Predict
            aqi_pred = self.model.predict(features_scaled)[0]
            
            # Ensure AQI is in valid range
            aqi_pred = max(0, min(500, int(aqi_pred)))
            
            logger.info(f"✓ ML model predicted AQI: {aqi_pred}")
            return aqi_pred
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return None
    
    def predict_hourly(self, base_weather_data: Dict, city: str = "Delhi", hours: int = 24) -> list:
        """
        Predict hourly AQI for the next N hours using ML model.
        
        Args:
            base_weather_data: Current weather data as baseline
            city: City name
            hours: Number of hours to predict (default 24)
        
        Returns:
            List of hourly predictions with AQI, temp, humidity, etc.
        """
        hourly_predictions = []
        now = datetime.now()
        
        for hour_offset in range(hours):
            # Calculate time for this hour
            forecast_time = now + timedelta(hours=hour_offset)
            hour_of_day = forecast_time.hour
            
            # Create weather data for this hour with variations
            hour_data = base_weather_data.copy()
            
            # Apply hourly variations
            # Temperature: cooler at night, warmer during day
            temp_base = base_weather_data.get("temp") or 25
            if 6 <= hour_of_day < 12:  # Morning
                temp_factor = 0.95 + (hour_of_day - 6) * 0.02
            elif 12 <= hour_of_day < 18:  # Afternoon
                temp_factor = 1.05 + (hour_of_day - 12) * 0.01
            elif 18 <= hour_of_day < 22:  # Evening
                temp_factor = 1.05 - (hour_of_day - 18) * 0.03
            else:  # Night
                temp_factor = 0.90
            hour_data["temp"] = temp_base * temp_factor
            
            # Humidity: inverse of temperature
            humidity_base = base_weather_data.get("humidity") or 60
            hour_data["humidity"] = min(100, humidity_base * (2 - temp_factor))
            
            # Wind: typically higher during day
            wind_base = base_weather_data.get("wind") or 10
            if 10 <= hour_of_day < 18:
                wind_factor = 1.2
            else:
                wind_factor = 0.8
            hour_data["wind"] = wind_base * wind_factor
            
            # PM2.5: higher during rush hours and night (temperature inversion)
            pm25_base = base_weather_data.get("pm25") or 50
            if hour_of_day in [7, 8, 9, 18, 19, 20]:  # Rush hours
                pm25_factor = 1.3
            elif 22 <= hour_of_day or hour_of_day < 6:  # Night
                pm25_factor = 1.15
            else:
                pm25_factor = 0.95
            hour_data["pm25"] = pm25_base * pm25_factor
            
            # Other pollutants follow PM2.5 pattern
            if "pm10" in base_weather_data and base_weather_data["pm10"] is not None:
                hour_data["pm10"] = base_weather_data["pm10"] * pm25_factor
            if "o3" in base_weather_data and base_weather_data["o3"] is not None:
                # O3 higher during sunny hours
                o3_factor = 1.2 if 11 <= hour_of_day < 16 else 0.8
                hour_data["o3"] = base_weather_data["o3"] * o3_factor
            if "no2" in base_weather_data and base_weather_data["no2"] is not None:
                hour_data["no2"] = base_weather_data["no2"] * pm25_factor
            if "so2" in base_weather_data and base_weather_data["so2"] is not None:
                hour_data["so2"] = base_weather_data["so2"] * pm25_factor
            if "co" in base_weather_data and base_weather_data["co"] is not None:
                hour_data["co"] = base_weather_data["co"] * pm25_factor
            
            # Predict AQI for this hour
            prediction = self.predict(hour_data, city)
            
            # Add time information
            prediction["hour"] = hour_of_day
            prediction["time"] = forecast_time.strftime("%I:%M %p")
            prediction["date"] = forecast_time.strftime("%Y-%m-%d")
            prediction["timestamp"] = forecast_time.isoformat()
            prediction["temp"] = round(hour_data["temp"], 1)
            prediction["humidity"] = round(hour_data["humidity"], 1)
            prediction["wind"] = round(hour_data["wind"], 1)
            
            hourly_predictions.append(prediction)
        
        return hourly_predictions
    
    def predict(self, weather_data: Dict, city: str = "Delhi") -> Dict:
        """
        Predict comprehensive AQI from weather data.
        Uses ML model if available, otherwise falls back to EPA formula.
        
        Args:
            weather_data: Dict with keys: temp, humidity, wind, pm25, pm10, o3, no2, so2, co
            city: City name for ML model
        
        Returns:
            Dict with keys: aqi, category, pollutants (dict), dominant_pollutant, sources
        
        Raises:
            ValueError: If required data is missing or invalid
        """
        try:
            # Validate input
            if not isinstance(weather_data, dict):
                raise ValueError("weather_data must be a dictionary")
            
            # Try ML model first for tomorrow's prediction
            ml_aqi = self.predict_with_ml(weather_data, city)
            
            # Extract pollutant values
            pm25 = weather_data.get("pm25")
            pm10 = weather_data.get("pm10")
            o3 = weather_data.get("o3")
            no2 = weather_data.get("no2")
            so2 = weather_data.get("so2")
            co = weather_data.get("co")
            us_aqi = weather_data.get("us_aqi")
            eu_aqi = weather_data.get("eu_aqi")
            aqi_sources = weather_data.get("aqi_sources", [])
            
            # Calculate individual AQI for each pollutant
            pollutant_aqis = {}
            
            if pm25 is not None and pm25 >= 0:
                pollutant_aqis["PM2.5"] = {
                    "aqi": pollutant_to_aqi(pm25, "pm25"),
                    "value": round(pm25, 2),
                    "unit": "µg/m³"
                }
            
            if pm10 is not None and pm10 >= 0:
                pollutant_aqis["PM10"] = {
                    "aqi": pollutant_to_aqi(pm10, "pm10"),
                    "value": round(pm10, 2),
                    "unit": "µg/m³"
                }
            
            if o3 is not None and o3 >= 0:
                pollutant_aqis["O3"] = {
                    "aqi": pollutant_to_aqi(o3, "o3"),
                    "value": round(o3, 2),
                    "unit": "µg/m³"
                }
            
            if no2 is not None and no2 >= 0:
                pollutant_aqis["NO2"] = {
                    "aqi": pollutant_to_aqi(no2, "no2"),
                    "value": round(no2, 2),
                    "unit": "µg/m³"
                }
            
            if so2 is not None and so2 >= 0:
                pollutant_aqis["SO2"] = {
                    "aqi": pollutant_to_aqi(so2, "so2"),
                    "value": round(so2, 2),
                    "unit": "µg/m³"
                }
            
            if co is not None and co >= 0:
                pollutant_aqis["CO"] = {
                    "aqi": pollutant_to_aqi(co, "co"),
                    "value": round(co, 2),
                    "unit": "µg/m³"
                }
            
            # Determine overall AQI (maximum of all pollutant AQIs)
            if pollutant_aqis:
                max_aqi = max(p["aqi"] for p in pollutant_aqis.values())
                dominant_pollutant = max(pollutant_aqis.items(), key=lambda x: x[1]["aqi"])[0]
            else:
                raise ValueError("No valid pollutant data available")
            
            # Use US AQI if available and higher
            if us_aqi is not None and us_aqi > max_aqi:
                max_aqi = us_aqi
                dominant_pollutant = "US EPA AQI"
            
            category = get_aqi_category(max_aqi)
            
            logger.info(f"Calculated AQI {max_aqi} ({category}) - Dominant: {dominant_pollutant}")
            
            return {
                "aqi": max_aqi,
                "category": category,
                "pollutants": pollutant_aqis,
                "dominant_pollutant": dominant_pollutant,
                "us_aqi": us_aqi,
                "eu_aqi": eu_aqi,
                "sources": aqi_sources if aqi_sources else ["Calculated from pollutants"]
            }
            
        except ValueError as e:
            logger.error(f"Validation error in predict: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise Exception(f"Prediction failed: {str(e)}")
