"""
ML Model Training Script for AgenticWeatherAI

This script fetches historical weather data from Open-Meteo Archive API,
trains a Prophet model to predict PM2.5 (and thus AQI), and saves the model
along with cached historical data.

Requirements: 6.1, 6.2, 6.3
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import joblib
import os
import time
from prophet import Prophet


class WeatherDataFetcher:
    """Handles fetching historical weather data from Open-Meteo Archive API"""
    
    def __init__(self, lat=19.07, lon=72.87, days=730):
        """
        Initialize the data fetcher
        
        Args:
            lat: Latitude (default: Mumbai)
            lon: Longitude (default: Mumbai)
            days: Number of historical days to fetch (default: 730)
        """
        self.lat = lat
        self.lon = lon
        self.days = days
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        
    def fetch_historical_data(self, max_retries=3, retry_delay=5):
        """
        Fetch historical weather data with retry logic
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            pandas.DataFrame with historical weather data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,pm2_5,pm10",
            "timezone": "auto"
        }
        
        for attempt in range(max_retries):
            try:
                print(f"Fetching historical data (attempt {attempt + 1}/{max_retries})...")
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse the response into a DataFrame
                df = self._parse_response(data)
                print(f"Successfully fetched {len(df)} hourly records")
                return df
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to fetch data after {max_retries} attempts")
    
    def _parse_response(self, data):
        """Parse Open-Meteo API response into DataFrame"""
        hourly = data.get("hourly", {})
        
        df = pd.DataFrame({
            "datetime": pd.to_datetime(hourly["time"]),
            "temperature": hourly["temperature_2m"],
            "humidity": hourly["relative_humidity_2m"],
            "wind_speed": hourly["wind_speed_10m"],
            "pm2_5": hourly["pm2_5"],
            "pm10": hourly["pm10"]
        })
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df


class ProphetModelTrainer:
    """Handles training the Prophet model for PM2.5 prediction"""
    
    def __init__(self):
        self.model = None
        
    def prepare_data(self, df):
        """
        Prepare data for Prophet training
        
        Args:
            df: DataFrame with historical weather data
            
        Returns:
            DataFrame formatted for Prophet (ds, y, regressors)
        """
        # Aggregate hourly data to daily (using noon values or mean)
        df['date'] = df['datetime'].dt.date
        daily_df = df.groupby('date').agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'wind_speed': 'mean',
            'pm2_5': 'mean',
            'pm10': 'mean'
        }).reset_index()
        
        # Format for Prophet
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(daily_df['date']),
            'y': daily_df['pm2_5'],  # Target variable
            'temperature': daily_df['temperature'],
            'humidity': daily_df['humidity'],
            'wind_speed': daily_df['wind_speed'],
            'pm10': daily_df['pm10']
        })
        
        # Remove any remaining NaN values
        prophet_df = prophet_df.dropna()
        
        print(f"Prepared {len(prophet_df)} daily records for training")
        return prophet_df
    
    def train_model(self, prophet_df):
        """
        Train Prophet model with regressors
        
        Args:
            prophet_df: DataFrame formatted for Prophet
            
        Returns:
            Trained Prophet model
        """
        print("Initializing Prophet model...")
        
        # Configure Prophet with seasonality
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05
        )
        
        # Add regressors
        print("Adding regressors: temperature, humidity, wind_speed, pm10")
        self.model.add_regressor('temperature')
        self.model.add_regressor('humidity')
        self.model.add_regressor('wind_speed')
        self.model.add_regressor('pm10')
        
        # Train the model
        print("Training model (this may take a few minutes)...")
        self.model.fit(prophet_df)
        
        print("Model training complete!")
        return self.model


class ModelPersistence:
    """Handles saving model and caching data"""
    
    def __init__(self, model_dir="backend/ml", cache_dir="backend/cache"):
        self.model_dir = model_dir
        self.cache_dir = cache_dir
        
        # Create directories if they don't exist
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def save_model(self, model, filename="model.pkl"):
        """
        Save trained Prophet model using joblib
        
        Args:
            model: Trained Prophet model
            filename: Name of the model file
        """
        model_path = os.path.join(self.model_dir, filename)
        print(f"Saving model to {model_path}...")
        joblib.dump(model, model_path)
        print("Model saved successfully!")
    
    def cache_historical_data(self, df, days=100, filename="historical.json"):
        """
        Cache last N days of historical data
        
        Args:
            df: DataFrame with historical weather data
            days: Number of recent days to cache
            filename: Name of the cache file
        """
        # Get last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_df = df[df['datetime'] >= cutoff_date].copy()
        
        # Convert to JSON-serializable format
        cache_data = {
            "last_updated": datetime.now().isoformat(),
            "days_cached": days,
            "records": recent_df.to_dict(orient='records')
        }
        
        # Convert datetime objects to strings
        for record in cache_data['records']:
            if 'datetime' in record:
                record['datetime'] = record['datetime'].isoformat()
        
        cache_path = os.path.join(self.cache_dir, filename)
        print(f"Caching last {days} days ({len(recent_df)} records) to {cache_path}...")
        
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print("Historical data cached successfully!")


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("AgenticWeatherAI - ML Model Training Pipeline")
    print("=" * 60)
    print()
    
    # Step 1: Fetch historical data
    print("Step 1: Fetching historical weather data...")
    fetcher = WeatherDataFetcher(lat=19.07, lon=72.87, days=730)
    df = fetcher.fetch_historical_data()
    print()
    
    # Step 2: Train Prophet model
    print("Step 2: Training Prophet model...")
    trainer = ProphetModelTrainer()
    prophet_df = trainer.prepare_data(df)
    model = trainer.train_model(prophet_df)
    print()
    
    # Step 3: Save model and cache data
    print("Step 3: Saving model and caching data...")
    persistence = ModelPersistence()
    persistence.save_model(model)
    persistence.cache_historical_data(df, days=100)
    print()
    
    print("=" * 60)
    print("Training pipeline completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Model saved to: backend/ml/model.pkl")
    print("2. Historical data cached to: backend/cache/historical.json")
    print("3. You can now start the FastAPI backend")


if __name__ == "__main__":
    main()
