# ML Training for AgenticWeatherAI

This folder contains the machine learning training pipeline for AQI prediction using the `city_day.csv` dataset.

## 📁 Files

- **city_day.csv** - Historical AQI data for Indian cities (2015-2020)
- **train_improved_model.py** - Python script for training models (LSTM + Traditional ML)
- **aqi_improved.ipynb** - Jupyter notebook for interactive training and analysis
- **aqi-aadil.ipynb** - Original notebook (legacy)
- **requirements_ml.txt** - Python dependencies for ML training

## 🎯 Features

### Training Coverage
- **ALL CITIES** - Trains on all ~26 cities in the dataset
- **No filtering** - Uses complete dataset for maximum generalization
- **~29,000 samples** - Comprehensive training data

### Models Trained
1. **LSTM (Long Short-Term Memory)** - Deep learning for temporal patterns
2. **Random Forest** - Ensemble learning with feature importance
3. **Gradient Boosting** - Advanced boosting algorithm

### Pollutants Analyzed
- PM2.5, PM10 (Particulate Matter)
- NO, NO2, NOx (Nitrogen compounds)
- SO2 (Sulfur Dioxide)
- CO (Carbon Monoxide)
- O3 (Ozone)
- NH3 (Ammonia)
- Benzene, Toluene, Xylene (VOCs)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_ml.txt
```

For LSTM support (optional):
```bash
pip install tensorflow
```

### 2. Train Models

**Option A: Simple Python Script (Recommended)**
```bash
python train_all_cities.py
```

**Option B: Advanced with LSTM**
```bash
cd ..
python backend/ml/train_improved_model.py
```

**Option C: Jupyter Notebook (Interactive)**
```bash
jupyter notebook aqi_improved.ipynb
```

### 3. Verify Models

After training, check that these files exist in `backend/ml/`:
- `best_model.pkl` - Best performing traditional model
- `random_forest_model.pkl` - Random Forest model
- `gradient_boosting_model.pkl` - Gradient Boosting model
- `scaler.pkl` - Feature scaler
- `lstm_model.h5` - LSTM model (if TensorFlow installed)
- `lstm_scaler.pkl` - LSTM feature scaler
- `model_metadata.json` - Training metadata

## 📊 Dataset Information

### city_day.csv Structure
```
City, Date, PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, 
Benzene, Toluene, Xylene, AQI, AQI_Bucket
```

### Data Range
- **Period**: 2015-2020
- **Cities**: 26 Indian cities
- **Records**: ~29,000 daily measurements
- **Training**: ALL cities (no filtering)

### AQI Categories
- **Good**: 0-50
- **Satisfactory**: 51-100
- **Moderate**: 101-200
- **Poor**: 201-300
- **Very Poor**: 301-400
- **Severe**: 401-500

## 🔬 Model Performance

### Expected Results

**Random Forest:**
- RMSE: ~15-25 AQI points
- R² Score: ~0.85-0.92
- Training Time: 2-5 minutes

**Gradient Boosting:**
- RMSE: ~18-28 AQI points
- R² Score: ~0.82-0.90
- Training Time: 5-10 minutes

**LSTM:**
- RMSE: ~20-30 AQI points
- R² Score: ~0.80-0.88
- Training Time: 10-30 minutes (depends on GPU)

### City-Specific Performance

The model is trained on all cities, providing:
- **Generalization** across different pollution patterns
- **Robustness** to various geographic and climatic conditions
- **Flexibility** to predict AQI for any Indian city

Top performing cities typically have:
- More consistent data collection
- Stable pollution patterns
- Sufficient historical records

## 🛠️ Customization

### Modify Training Parameters

Edit `backend/ml/train_improved_model.py`:

```python
# Random Forest
RandomForestRegressor(
    n_estimators=200,  # Increase for better accuracy
    max_depth=20,      # Adjust tree depth
    random_state=42
)

# LSTM
lstm_trainer.train(
    epochs=50,         # Increase for better convergence
    batch_size=32      # Adjust based on memory
)
```

### Filter Specific Cities (if needed)

```python
# By default trains on all cities
# To filter specific cities, modify load_and_clean_data():
target_cities = ['Delhi', 'Mumbai', 'Pune']
df = df[df['City'].isin(target_cities)]
```

### Change Features

```python
feature_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
# Remove or add pollutants as needed
```

## 📈 Visualization

The Jupyter notebook includes:
- AQI distribution by city
- Temporal trends over years
- Pollutant correlation heatmaps
- Feature importance analysis
- Prediction vs Actual scatter plots
- City-specific performance metrics

## 🐛 Troubleshooting

### TensorFlow Not Available
```bash
# Install TensorFlow
pip install tensorflow

# Or CPU-only version (smaller, no GPU needed)
pip install tensorflow-cpu
```

### Memory Issues
```python
# Reduce batch size in LSTM training
lstm_trainer.train(batch_size=16)  # Default is 32

# Or reduce sequence length
processor.create_sequences_for_lstm(sequence_length=5)  # Default is 7
```

### Missing Data
```python
# Check dataset path
processor = DataProcessor(csv_path="ML/city_day.csv")

# Verify file exists
import os
print(os.path.exists("ML/city_day.csv"))
```

## 📝 Notes

1. **Data Quality**: The city_day.csv dataset has some missing values. The training script handles this with forward/backward fill and median imputation.

2. **Temporal Split**: We use temporal splitting (no shuffle) to maintain time-series integrity. This is more realistic for forecasting.

3. **Feature Scaling**: StandardScaler is used to normalize features. The scaler is saved for use during prediction.

4. **Model Selection**: The best model is automatically selected based on R² score on the test set.

5. **LSTM Sequences**: LSTM uses 7-day sequences to capture weekly patterns in air quality.

## 🔗 Integration

After training, the models are automatically saved to `backend/ml/` and can be used by:
- `backend/agents/predictor.py` - Main prediction agent
- `backend/main.py` - FastAPI endpoints

The predictor will automatically load the best available model.

## 📚 References

- **Dataset Source**: Kaggle - India Air Quality Data
- **AQI Standards**: Central Pollution Control Board (CPCB), India
- **EPA AQI**: US Environmental Protection Agency standards

## 👨‍💻 Author

**AADIL SHAIKH** - AgenticWeatherAI Project

---

**Happy Training! 🚀**
