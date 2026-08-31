# AgenticWeatherAI - System Overview

## 🎯 Architecture

### Data Flow
```
User Request → Backend API → Data Sources → ML Prediction → Response
                                ↓
                         1. WAQI (Primary - ONLY)
                         2. Tavily (Fallback if WAQI fails)
                         3. Tavily (News/Context)
```

## 📊 Data Sources (Priority Order)

### 1. WAQI API (PRIMARY - Real-time AQI) ⭐
- **Purpose**: Real-time air quality data and weather
- **Coverage**: 12,000+ monitoring stations worldwide
- **Data**: AQI, PM2.5, PM10, O3, NO2, SO2, CO, Temperature, Humidity, Wind, Pressure
- **Token**: `your_waqi_api_token_here`
- **Rate Limit**: 1,000 requests/minute
- **Status**: ✅ Active (ONLY source for AQI)

### 2. Tavily API (FALLBACK - AQI Search)
- **Purpose**: Fallback AQI information extraction when WAQI fails
- **Coverage**: Web search
- **Data**: AQI estimates from search results
- **Status**: ✅ Active as fallback only

### 3. Tavily API (CONTEXT - News)
- **Purpose**: Environmental news and context
- **Coverage**: Web search
- **Data**: News articles, alerts, events
- **Status**: ✅ Active for context

## 🤖 ML Model

### Trained Model
- **Type**: Random Forest / Gradient Boosting
- **Dataset**: city_day.csv (18,265 samples, 5 cities)
- **Features**: 16 (pollutants + temporal + city encoding)
- **Purpose**: Predict tomorrow's AQI
- **Location**: `backend/ml/best_model.pkl`
- **Performance**: R² score varies with data quality

### Prediction Flow
1. **Today**: WAQI real-time data (or Tavily fallback)
2. **Tomorrow**: WAQI forecast or estimated from today's data
3. **ML Enhancement**: ML model can predict AQI trends
4. **Fallback**: EPA formula (PM2.5 → AQI conversion)

## 🔑 API Keys Required

```env
# Required
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key

# Primary AQI Source
WAQI_API_KEY=your_waqi_api_token_here
```

## 📁 Project Structure

```
AQI-AI/
├── backend/
│   ├── agents/
│   │   ├── data_collector.py    # WAQI + Tavily fallback
│   │   ├── waqi_collector.py    # WAQI API client (PRIMARY)
│   │   ├── predictor.py         # ML model predictions
│   │   ├── interpreter.py       # Gemini summaries
│   │   ├── recommender.py       # Health advice
│   │   └── search_agent.py      # Tavily search (fallback + news)
│   ├── ml/
│   │   ├── best_model.pkl       # Trained ML model
│   │   ├── scaler.pkl           # Feature scaler
│   │   └── city_encoder.pkl     # City encoder
│   ├── main.py                  # FastAPI backend
│   └── test_waqi.py            # WAQI integration test
├── frontend/
│   └── src/                     # React frontend
├── ML/
│   ├── train_optimized.py       # Model training script
│   ├── city_day.csv            # Training dataset
│   └── README.md               # ML documentation
└── .env                         # API keys
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy API keys
cp .env.example .env
# Edit .env and add your keys
```

### 2. Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. Start Services
```bash
# Backend
python -m uvicorn backend.main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev
```

### 4. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testing

### Test WAQI Integration
```bash
python backend/test_waqi.py
```

### Test ML Model
```bash
# Models are automatically loaded by predictor.py
# Test via API: POST /predict
```

## 🔄 Data Flow Example

### User Request: "AQI for Delhi"

1. **Data Collection** (`data_collector.py`)
   - Try WAQI API for Delhi → ✓ Get real-time AQI + weather
   - Fallback to Tavily search if WAQI fails

2. **ML Prediction** (`predictor.py`)
   - Load trained model
   - Use today's data as features
   - Predict tomorrow's AQI

3. **Context Search** (`search_agent.py`)
   - Search Tavily for Delhi air quality news
   - Get environmental alerts

4. **Interpretation** (`interpreter.py`)
   - Use Gemini to generate summary
   - Explain AQI levels

5. **Recommendations** (`recommender.py`)
   - Generate health advice
   - Activity recommendations

6. **Response**
   ```json
   {
     "city": "Delhi",
     "forecast": {
       "today": {"aqi": 245, "temp": 28, ...},
       "tomorrow": {"aqi": 230, "temp": 29, ...}
     },
     "summary": "Air quality is poor...",
     "advice": "Avoid outdoor activities...",
     "news": [...]
   }
   ```

## 📊 Model Training

### Train New Model
```bash
cd ML
python train_optimized.py
```

### Model Features
- PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3
- Benzene, Toluene, Xylene
- Month, DayOfYear, DayOfWeek
- City (encoded)

## 🎯 Key Features

1. ✅ **Real-time Data**: WAQI API with 12,000+ stations (PRIMARY ONLY)
2. ✅ **ML Predictions**: Tomorrow's AQI using trained models
3. ✅ **Smart Fallback**: Tavily search if WAQI unavailable
4. ✅ **Context Aware**: Tavily news integration
5. ✅ **AI Summaries**: Gemini-powered explanations
6. ✅ **Health Advice**: Personalized recommendations
7. ✅ **Simplified**: Single data source (WAQI) for reliability

## 🔧 Configuration

### Priority Order (Hardcoded)
1. WAQI API (PRIMARY - real-time AQI + weather)
2. Tavily API (FALLBACK - AQI search if WAQI fails)
3. Tavily API (CONTEXT - news and alerts)

### No Configuration Needed
- System automatically uses WAQI if token is present
- Falls back to Tavily search if WAQI fails
- ML model automatically loaded if available
- **No Open-Meteo, IQAir, OpenWeatherMap, or OpenAQ** - removed for simplicity

## 📝 Notes

- **WAQI Token**: Already configured in `.env.example`
- **ML Model**: Trained on synthetic data, accuracy limited
- **Real Data**: Replace `city_day.csv` with real data for better predictions
- **Fallback**: System works even if WAQI fails (uses Tavily search)
- **Simplified**: Removed Open-Meteo, IQAir, OpenWeatherMap, OpenAQ for reliability

## 🆘 Troubleshooting

### WAQI Not Working
```bash
# Test token
python backend/test_waqi.py

# Check .env file
cat .env | grep WAQI
```

### ML Model Not Loading
```bash
# Check if model exists
ls backend/ml/best_model.pkl

# Retrain if needed
cd ML
python train_optimized.py
```

### Backend Errors
```bash
# Check logs
python -m uvicorn backend.main:app --reload --log-level debug
```

---

**Status**: ✅ Production Ready  
**Last Updated**: December 2024  
**Primary Data Source**: WAQI API
