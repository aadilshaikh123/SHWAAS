# 🌤️ AgenticWeatherAI

**Multi-agent AI system for weather forecasting and air quality prediction with personalized health recommendations.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

AgenticWeatherAI uses a multi-agent architecture to provide:
- **Real-time AQI data** from 12,000+ monitoring stations worldwide (WAQI API)
- **Tomorrow's weather forecast** with ML-powered predictions
- **Personalized health advice** based on air quality and user profile
- **Natural language summaries** powered by Google Gemini AI
- **Environmental news context** via Tavily search

### Key Features

✅ **Real-time Data**: WAQI API with global coverage  
✅ **24-Hour Forecast**: Hour-by-hour AQI predictions using ML models  
✅ **Smart Fallback**: Tavily search if WAQI unavailable  
✅ **ML Predictions**: Trained models for AQI forecasting  
✅ **AI-Powered**: Gemini API for natural language generation  
✅ **Comprehensive**: All major pollutants (PM2.5, PM10, O3, NO2, SO2, CO)  
✅ **User-Friendly**: Modern React frontend with beautiful UI  
✅ **Interactive**: Click on any hour to see detailed pollutant breakdown  

---

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│  - Location input                       │
│  - AQI visualization                    │
│  - Health recommendations               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       FastAPI Backend (Python)          │
│  - Multi-agent orchestration            │
│  - API endpoints                        │
│  - Error handling                       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│ WAQI API    │  │ Tavily API  │
│ (Primary)   │  │ (Fallback)  │
└─────────────┘  └─────────────┘
       │               │
       └───────┬───────┘
               ▼
┌─────────────────────────────────────────┐
│          Agent Pipeline                 │
│                                         │
│  1. DataCollector  → Fetch AQI data    │
│  2. Predictor      → ML predictions    │
│  3. SearchAgent    → News context      │
│  4. Interpreter    → AI summary        │
│  5. Recommender    → Health advice     │
└─────────────────────────────────────────┘
```

### Agents

| Agent | Purpose | Technology |
|-------|---------|------------|
| **DataCollector** | Fetch real-time AQI + weather | WAQI API → Tavily fallback |
| **Predictor** | Predict tomorrow's AQI | ML (Random Forest/Gradient Boosting) |
| **SearchAgent** | Get environmental news | Tavily Web Search |
| **Interpreter** | Generate summaries | Google Gemini API |
| **Recommender** | Health & activity advice | Google Gemini API |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### 1. Clone Repository

```bash
git clone <repository-url>
cd AgenticWeatherAI
```

### 2. Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
```

Required API keys:
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Primary AQI source (already configured)
WAQI_API_KEY=7616cb77c13b13fd483b76c94ae8ba422dc94e8c
```

**Get API Keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **Tavily**: https://tavily.com/
- **WAQI**: https://aqicn.org/data-platform/token/ (demo token included)

### 3. Install Dependencies

#### Backend
```bash
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
cd ..
```

### 4. Start Services

#### Option A: Using Start Scripts (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📊 Data Sources

### Primary: WAQI API ⭐

- **Coverage**: 12,000+ monitoring stations worldwide
- **Data**: AQI, PM2.5, PM10, O3, NO2, SO2, CO, Temperature, Humidity, Wind
- **Update Frequency**: Real-time
- **Rate Limit**: 1,000 requests/minute
- **Status**: ✅ Active

### Fallback: Tavily Search

- **Purpose**: Extract AQI from web search if WAQI fails
- **Coverage**: Global web search
- **Data**: Estimated AQI from search results
- **Status**: ✅ Active

### Context: Tavily News

- **Purpose**: Environmental news and alerts
- **Coverage**: News articles, weather events
- **Status**: ✅ Active

---

## 🤖 Machine Learning

### Model Details

- **Type**: Random Forest / Gradient Boosting / Extra Trees
- **Dataset**: city_day.csv (18,265 samples, 5 cities)
- **Features**: 16 features (pollutants + temporal + city encoding)
- **Target**: Tomorrow's AQI
- **Location**: `backend/ml/best_model.pkl`

### Training New Model

```bash
cd ML
python train_optimized.py
```

The script will:
1. Load and clean data from `city_day.csv`
2. Train multiple models (Random Forest, Gradient Boosting, Extra Trees)
3. Select best model based on R² score
4. Save model, scaler, and encoder to `backend/ml/`

### Model Features

- **Pollutants**: PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene
- **Temporal**: Month, DayOfYear, DayOfWeek
- **Location**: City (encoded)

---

## 📁 Project Structure

```
AgenticWeatherAI/
├── backend/
│   ├── agents/
│   │   ├── data_collector.py      # WAQI + Tavily integration
│   │   ├── waqi_collector.py      # WAQI API client
│   │   ├── predictor.py           # ML predictions
│   │   ├── interpreter.py         # Gemini summaries
│   │   ├── recommender.py         # Health advice
│   │   └── search_agent.py        # Tavily search
│   ├── ml/
│   │   ├── best_model.pkl         # Trained ML model
│   │   ├── scaler.pkl             # Feature scaler
│   │   └── city_encoder.pkl       # City encoder
│   ├── cache/                     # Cached API responses
│   ├── main.py                    # FastAPI application
│   └── test_waqi.py              # WAQI integration test
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm.jsx      # Location input
│   │   │   ├── ForecastDisplay.jsx # AQI display
│   │   │   └── LoadingSkeleton.jsx # Loading UI
│   │   ├── App.jsx                # Main app
│   │   └── main.jsx               # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── ML/
│   ├── train_optimized.py         # Model training script
│   ├── city_day.csv              # Training dataset
│   └── README.md                 # ML documentation
├── .env                           # API keys (create from .env.example)
├── .env.example                   # Example environment file
├── requirements.txt               # Python dependencies
├── start.bat                      # Windows start script
├── start.sh                       # Linux/Mac start script
├── README.md                      # This file
└── SYSTEM_OVERVIEW.md            # Technical documentation
```

---

## 🔧 API Endpoints

### POST /predict

Get weather forecast and AQI predictions for a city.

**Request:**
```json
{
  "city": "Delhi",
  "lat": 28.6139,
  "lon": 77.2090,
  "profile": "asthma, outdoor runner",
  "use_search": true
}
```

**Response:**
```json
{
  "city": "Delhi",
  "forecast": {
    "temp": 28.5,
    "humidity": 65,
    "wind": 12.3,
    "aqi": 245,
    "pm25": 145.2,
    "pm10": 210.5,
    "o3": 45.3,
    "no2": 52.1,
    "so2": 15.2,
    "co": 1200
  },
  "today_forecast": { ... },
  "hourly_forecast": [
    {
      "hour": 14,
      "time": "02:00 PM",
      "aqi": 245,
      "temp": 29.2,
      "humidity": 62,
      "wind": 13.5,
      "pollutants": { ... }
    },
    // ... 23 more hours
  ],
  "summary": "Tomorrow in Delhi: Air quality is poor with AQI 245...",
  "advice": "Avoid outdoor activities. Use N95 masks if going outside...",
  "search_results": { ... },
  "data_sources": ["WAQI API", "Tavily Search", "Google Gemini API"]
}
```

### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "agents": {
    "data_collector": true,
    "predictor": true,
    "interpreter": true,
    "recommender": true,
    "search_agent": true
  }
}
```

---

## 🧪 Testing

### Test WAQI Integration

```bash
python backend/test_waqi.py
```

Expected output:
```
Testing WAQI integration...
✓ Using WAQI real-time data
Weather data collected for tomorrow: temp=21.8°C, humidity=92.9%, pm25=138
AQI prediction: 194 (Unhealthy)
```

### Test API Endpoints

```bash
# Using curl
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "lat": 19.0760,
    "lon": 72.8777,
    "profile": "",
    "use_search": true
  }'

# Or visit API docs
open http://localhost:8000/docs
```

---

## 🎨 Frontend Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Real-time Search**: Location autocomplete with Mapbox
- **AQI Visualization**: Color-coded AQI levels with health categories
- **Pollutant Breakdown**: Detailed view of all pollutants
- **Health Advice**: Personalized recommendations
- **News Context**: Environmental news and alerts
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages

---

## 🔍 Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac
```

### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### WAQI API Not Working

```bash
# Test WAQI token
python backend/test_waqi.py

# Check .env file
cat .env | grep WAQI

# Verify token at https://aqicn.org/data-platform/token/
```

### ML Model Not Loading

```bash
# Check if model exists
ls backend/ml/best_model.pkl

# Retrain model
cd ML
python train_optimized.py
```

### API Returns Errors

```bash
# Check logs
python -m uvicorn backend.main:app --reload --log-level debug

# Verify all API keys in .env
cat .env
```

---

## 📝 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key | - |
| `TAVILY_API_KEY` | ✅ Yes | Tavily search API key | - |
| `WAQI_API_KEY` | ✅ Yes | WAQI API token | Demo token |

### Data Source Priority

1. **WAQI API** (Primary) - Real-time AQI from sensors
2. **Tavily Search** (Fallback) - Extract AQI from web if WAQI fails
3. **Cache** (Last resort) - Use cached data if both fail

---

## 🚧 Known Limitations

1. **ML Model Accuracy**: Trained on synthetic data, may not reflect real-world patterns
2. **WAQI Coverage**: Not all locations have nearby monitoring stations
3. **Tavily Fallback**: Estimated AQI may be less accurate than sensor data
4. **Rate Limits**: WAQI has 1,000 req/min limit (sufficient for most use cases)

---

## 🛠️ Development

### Adding New Features

1. **New Agent**: Create in `backend/agents/`
2. **New Endpoint**: Add to `backend/main.py`
3. **New Component**: Add to `frontend/src/components/`

### Code Style

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, Prettier
- **Commits**: Conventional commits

### Running Tests

```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm test
```

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📧 Support

- **Issues**: GitHub Issues
- **Documentation**: See `SYSTEM_OVERVIEW.md` for technical details
- **ML Training**: See `ML/README.md` for model training guide

---

## 🌟 Acknowledgments

- **WAQI**: World Air Quality Index Project
- **Tavily**: AI-powered search API
- **Google Gemini**: Natural language generation
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework

---

**Built with ❤️ for better air quality awareness**

🌍 Help people breathe easier with real-time AQI data and personalized health advice.
