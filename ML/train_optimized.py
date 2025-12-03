"""
Optimized AQI Model Training - Fast but Effective
Trains models with good hyperparameters without extensive grid search
"""

import pandas as pd
import numpy as np
import warnings
import joblib
import os
import json
from datetime import datetime
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

print("="*70)
print("OPTIMIZED AQI MODEL TRAINING")
print("="*70)

# Load data
print("\n[1/5] Loading...")
csv_path = 'city_day.csv' if os.path.exists('city_day.csv') else 'ML/city_day.csv'
df = pd.read_csv(csv_path)
print(f"✓ {df.shape[0]} rows, {df.shape[1]} columns")

# Detect columns
date_col = next((col for col in df.columns if col.lower() in ['date', 'datetime']), None)
city_col = next((col for col in df.columns if col.lower() == 'city'), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col])
    df['Month'] = df[date_col].dt.month
    df['DayOfYear'] = df[date_col].dt.dayofyear
    df['DayOfWeek'] = df[date_col].dt.dayofweek
else:
    df['Month'], df['DayOfYear'], df['DayOfWeek'] = 6, 150, 2

# Preprocess
print("\n[2/5] Preprocessing...")
numeric_cols = df.select_dtypes(include=[np.number]).columns
if city_col:
    df[numeric_cols] = df.groupby(city_col)[numeric_cols].fillna(method='ffill').fillna(method='bfill')
for col in numeric_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].median(), inplace=True)
print("✓ Clean")

# Features
print("\n[3/5] Features...")
feature_cols = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 
                'Benzene', 'Toluene', 'Xylene', 'Month', 'DayOfYear', 'DayOfWeek']
available_features = [col for col in feature_cols if col in df.columns]
X = df[available_features].copy()

if city_col:
    le = LabelEncoder()
    X['City_Encoded'] = le.fit_transform(df[city_col])
else:
    X['City_Encoded'], le = 0, None

y = df['AQI'].copy()

# Remove rows where AQI is 0 or features are all 0 (bad data)
valid_mask = (y > 0) & (X.sum(axis=1) > 0)
X = X[valid_mask]
y = y[valid_mask]

print(f"✓ {X.shape[1]} features, {len(X):,} samples (after cleaning)")

# Split - use shuffle=True for better generalization with synthetic data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Train: {len(X_train):,} | Test: {len(X_test):,}")
print(f"  Train AQI: {y_train.min():.1f} - {y_train.max():.1f} (mean: {y_train.mean():.1f})")
print(f"  Test AQI: {y_test.min():.1f} - {y_test.max():.1f} (mean: {y_test.mean():.1f})")

# Train models
print("\n[4/5] Training (3-5 min)...")

models = {
    'Random Forest': RandomForestRegressor(
        n_estimators=200, max_depth=20, min_samples_split=5,
        min_samples_leaf=2, max_features='sqrt', random_state=42, n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=200, max_depth=8, learning_rate=0.1,
        subsample=0.8, max_features='sqrt', random_state=42
    ),
    'Extra Trees': ExtraTreesRegressor(
        n_estimators=200, max_depth=20, min_samples_split=5,
        min_samples_leaf=2, max_features='sqrt', random_state=42, n_jobs=-1
    )
}

results = {}
for name, model in models.items():
    print(f"  {name}...", end=' ')
    model.fit(X_train_scaled, y_train)
    
    test_pred = model.predict(X_test_scaled)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    test_r2 = r2_score(y_test, test_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    
    results[name] = {
        'model': model,
        'rmse': test_rmse,
        'r2': test_r2,
        'mae': test_mae,
        'pred': test_pred
    }
    print(f"RMSE: {test_rmse:.2f}, R²: {test_r2:.4f}")

# Best model
best_name = max(results, key=lambda k: results[k]['r2'])
best = results[best_name]

print(f"\n🏆 Best: {best_name}")
print(f"   RMSE: {best['rmse']:.2f}")
print(f"   R²: {best['r2']:.4f}")
print(f"   MAE: {best['mae']:.2f}")

# Save
print("\n[5/5] Saving...")
os.makedirs('../backend/ml', exist_ok=True)

for name, res in results.items():
    safe_name = name.lower().replace(' ', '_')
    joblib.dump(res['model'], f'../backend/ml/{safe_name}_model.pkl')

joblib.dump(best['model'], '../backend/ml/best_model.pkl')
joblib.dump(scaler, '../backend/ml/scaler.pkl')
if le:
    joblib.dump(le, '../backend/ml/city_encoder.pkl')

metadata = {
    'training_date': datetime.now().isoformat(),
    'dataset_size': len(df),
    'n_cities': df[city_col].nunique() if city_col else 0,
    'features': list(X.columns),
    'best_model': best_name,
    'performance': {
        'test_rmse': float(best['rmse']),
        'test_r2': float(best['r2']),
        'test_mae': float(best['mae'])
    },
    'all_models': {
        name: {
            'test_rmse': float(res['rmse']),
            'test_r2': float(res['r2']),
            'test_mae': float(res['mae'])
        }
        for name, res in results.items()
    }
}

with open('../backend/ml/model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("✓ All models saved")

print("\n" + "="*70)
print("✅ COMPLETE!")
print("="*70)
print(f"\nBest Model: {best_name}")
print(f"Test RMSE: {best['rmse']:.2f} AQI points")
print(f"Test R²: {best['r2']:.4f}")
print(f"\nModels saved to: backend/ml/")
print("="*70)
