"""
AgenticWeatherAI - FastAPI Backend
Main application file with API endpoints and agent orchestration
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional
import os
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Windows consoles default to cp1252; agent prints use non-ASCII glyphs and would
# otherwise raise UnicodeEncodeError mid-request.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load environment variables from .env file
load_dotenv()

# Import agents
from backend.agents.data_collector import DataCollectorAgent
from backend.agents.predictor import PredictorAgent
from backend.agents.interpreter import InterpreterAgent
from backend.agents.recommender import RecommenderAgent
from backend.agents.search_agent import SearchAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgenticWeatherAI",
    description="Multi-agent AI system for weather and AQI prediction",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for agents
data_collector = None
predictor = None
interpreter = None
recommender = None
search_agent = None


# Pydantic models for request and response
class SearchResults(BaseModel):
    """Search results model"""
    summary: str = Field(..., description="Brief summary of search findings")
    sources: list[str] = Field(..., description="Source URLs")
    relevant: bool = Field(..., description="Whether results are relevant")


class PredictionRequest(BaseModel):
    """Request model for /predict endpoint"""
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    profile: Optional[str] = Field("", max_length=200, description="Optional user health/activity profile")
    use_search: bool = Field(False, description="Enable/disable web search for additional context (news only, not for AQI data)")
    
    @validator('city')
    def validate_city(cls, v):
        """Validate city name contains only alphanumeric, spaces, and hyphens"""
        if not all(c.isalnum() or c.isspace() or c == '-' for c in v):
            raise ValueError('City name must contain only letters, numbers, spaces, and hyphens')
        return v.strip()
    
    @validator('profile')
    def validate_profile(cls, v):
        """Validate and clean profile string"""
        if v:
            return v.strip()
        return ""


class ForecastData(BaseModel):
    """Forecast data model"""
    temp: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    wind: float = Field(..., description="Wind speed in km/h")
    aqi: int = Field(..., description="Air Quality Index")


class PredictionResponse(BaseModel):
    """Response model for /predict endpoint"""
    city: str = Field(..., description="City name")
    forecast: ForecastData = Field(..., description="Weather and AQI forecast")
    summary: str = Field(..., description="Natural language summary")
    advice: str = Field(..., description="Health and activity recommendations")
    search_results: Optional[SearchResults] = Field(None, description="Web search results for additional context")
    data_sources: list[str] = Field(..., description="List of data sources used")


def validate_environment():
    """
    Validate required environment variables at startup.
    
    Raises:
        EnvironmentError: If required environment variables are missing
    """
    required_vars = {
        "GEMINI_API_KEY": "Google Gemini API key for natural language generation",
        "TAVILY_API_KEY": "Tavily API key for web search functionality"
    }
    
    missing_vars = []
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value or value.strip() == "":
            missing_vars.append(f"  - {var_name}: {description}")
    
    if missing_vars:
        error_message = (
            "Missing required environment variables:\n" +
            "\n".join(missing_vars) +
            "\n\nPlease set them in your .env file or environment.\n" +
            "See .env.example for reference."
        )
        logger.error(error_message)
        raise EnvironmentError(error_message)
    
    logger.info("Environment validation passed - all required API keys present")


@app.on_event("startup")
async def startup_event():
    """
    Initialize agents and load ML model at startup.
    Validates environment variables and initializes all agents with appropriate API keys.
    """
    global data_collector, predictor, interpreter, recommender, search_agent
    
    try:
        logger.info("Initializing AgenticWeatherAI backend...")
        
        # Validate required environment variables
        validate_environment()
        
        # Get API keys from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        waqi_api_key = os.getenv("WAQI_API_KEY") or os.getenv("WAQI_TOKEN")
        
        logger.info("API keys loaded from environment")
        
        # Initialize all agents with appropriate keys
        logger.info("Initializing DataCollector agent...")
        if waqi_api_key:
            logger.info("WAQI API key found - using WAQI for real-time AQI data")
        else:
            logger.warning("No WAQI API key - will rely on Tavily fallback only")
        data_collector = DataCollectorAgent()
        
        logger.info("Initializing Predictor agent...")
        predictor = PredictorAgent(model_path="backend/ml/model.pkl")
        
        logger.info("Initializing Interpreter agent with Gemini API...")
        interpreter = InterpreterAgent(gemini_api_key=gemini_api_key)
        
        logger.info("Initializing Recommender agent with Gemini API...")
        recommender = RecommenderAgent(gemini_api_key=gemini_api_key)
        
        logger.info("Initializing SearchAgent with Tavily API...")
        search_agent = SearchAgent(tavily_api_key=tavily_api_key)
        
        logger.info("All agents initialized successfully!")
        
    except EnvironmentError as e:
        logger.error(f"Environment validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve API information. Frontend is served separately via Vite dev server.
    """
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AgenticWeatherAI API</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                }
                h1 { font-size: 2.5em; margin-bottom: 10px; }
                a {
                    color: #ffd700;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover { text-decoration: underline; }
                .endpoint {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                }
                code {
                    background: rgba(0, 0, 0, 0.3);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌤️ AgenticWeatherAI API</h1>
                <p><strong>Multi-agent AI system for weather and AQI prediction</strong></p>
                
                <h2>🚀 Quick Start</h2>
                <p>Frontend: <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p>
                <p>API Docs: <a href="/docs">/docs</a></p>
                
                <h2>📡 API Endpoints</h2>
                <div class="endpoint">
                    <strong>POST /predict</strong><br>
                    Get weather forecast and AQI predictions
                </div>
                <div class="endpoint">
                    <strong>GET /health</strong><br>
                    Check API health status
                </div>
                
                <h2>💡 Usage</h2>
                <p>1. Start the frontend: <code>cd frontend && npm run dev</code></p>
                <p>2. Visit <a href="http://localhost:3000">http://localhost:3000</a></p>
                <p>3. Enter a location and get AI-powered predictions!</p>
            </div>
        </body>
        </html>
        """,
        status_code=200
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    try:
        # Check if agents are initialized
        agents_status = {
            "data_collector": data_collector is not None,
            "predictor": predictor is not None,
            "interpreter": interpreter is not None,
            "recommender": recommender is not None,
            "search_agent": search_agent is not None
        }
        
        all_healthy = all(agents_status.values())
        
        return JSONResponse(
            content={
                "status": "healthy" if all_healthy else "degraded",
                "agents": agents_status
            },
            status_code=200 if all_healthy else 503
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )


@app.post("/predict")
def predict(request: PredictionRequest):
    """
    Predict tomorrow's weather and AQI for a given city.
    
    Orchestrates the multi-agent workflow:
    1. DataCollector: Fetch weather data from Open-Meteo API
    2. Predictor: Calculate AQI from PM2.5 data
    3. SearchAgent: Get real-time weather context (optional)
    4. Interpreter: Generate natural language summary (with search context)
    5. Recommender: Provide personalized health advice (with search context)
    
    Args:
        request: PredictionRequest with city, lat, lon, optional profile, and use_search flag
    
    Returns:
        PredictionResponse with forecast, summary, advice, search results, and data sources
    
    Raises:
        HTTPException: For various error conditions
    """
    # Track data sources for attribution
    data_sources = []
    search_results_data = None
    search_context = None
    
    try:
        logger.info(f"Processing prediction request for {request.city} ({request.lat}, {request.lon}), use_search={request.use_search}")
        
        # Check if agents are initialized
        if not all([data_collector, predictor, interpreter, recommender]):
            logger.error("Core agents not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Core agents not initialized. Please check API key configuration and try again."
            )
        
        # Step 1: Collect weather data for today and tomorrow
        logger.info("Step 1: Collecting weather data for today and tomorrow...")
        try:
            multi_day_data = data_collector.collect_data_multi_day(
                city=request.city,
                lat=request.lat,
                lon=request.lon
            )
            
            today_data = multi_day_data.get("today")
            tomorrow_data = multi_day_data.get("tomorrow")
            
            # Track data source
            source = multi_day_data.get("source", "Unknown")
            if source == "WAQI":
                data_sources.append("WAQI API")
            elif source == "Tavily":
                data_sources.append("Tavily Search")
            elif source.startswith("cache"):
                data_sources.append("Cache")
            
            logger.info(f"Weather data collected for tomorrow: temp={tomorrow_data.get('temp')}°C, humidity={tomorrow_data.get('humidity')}%, pm25={tomorrow_data.get('pm25')}")
            if today_data:
                logger.info(f"Weather data collected for today: temp={today_data.get('temp')}°C, humidity={today_data.get('humidity')}%, pm25={today_data.get('pm25')}")
            
            # Use tomorrow's data for main prediction (backward compatibility)
            weather_data = tomorrow_data
            
            # Validate weather data ranges
            if not (-50 <= weather_data.get('temp', 0) <= 60):
                logger.warning(f"Temperature out of realistic range: {weather_data.get('temp')}°C")
            if not (0 <= weather_data.get('humidity', 0) <= 100):
                logger.warning(f"Humidity out of valid range: {weather_data.get('humidity')}%")
            if weather_data.get('wind', 0) < 0:
                logger.warning(f"Wind speed is negative: {weather_data.get('wind')} km/h")
                
        except Exception as e:
            logger.error(f"DataCollector failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch weather data. Please check your coordinates and API keys. Error: {str(e)}"
            )
        
        # Step 2: Predict AQI
        logger.info("Step 2: Predicting AQI...")
        try:
            aqi_data = predictor.predict(weather_data)
            logger.info(f"AQI prediction: {aqi_data.get('aqi')} ({aqi_data.get('category', 'Unknown')})")
            
            # Validate AQI data
            if aqi_data.get('aqi', 0) < 0 or aqi_data.get('aqi', 0) > 500:
                logger.warning(f"AQI out of valid range: {aqi_data.get('aqi')}")
                
        except Exception as e:
            logger.error(f"Predictor failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate AQI from weather data. Error: {str(e)}"
            )
        
        # Combine forecast data with all pollutants
        forecast_data = {
            "temp": weather_data.get("temp"),
            "humidity": weather_data.get("humidity"),
            "wind": weather_data.get("wind"),
            "aqi": aqi_data.get("aqi"),
            "pollutants": aqi_data.get("pollutants", {}),
            "dominant_pollutant": aqi_data.get("dominant_pollutant"),
            "us_aqi": aqi_data.get("us_aqi"),
            "eu_aqi": aqi_data.get("eu_aqi")
        }
        
        # Step 3: Search for weather context (if enabled)
        if request.use_search and search_agent:
            logger.info("Step 3: Searching for weather context...")
            try:
                search_results = search_agent.search_weather_context(
                    city=request.city,
                    date="tomorrow"
                )
                
                if search_results.get("relevant"):
                    logger.info(f"Search results found: {len(search_results.get('results', []))} articles")
                    search_results_data = search_results  # Use dict directly
                    # Create context string for agents
                    search_context = search_results.get("summary", "")
                    data_sources.append("Tavily Web Search")
                else:
                    logger.info("No relevant search results found")
                    
            except Exception as e:
                # Gracefully degrade - continue without search results
                logger.warning(f"SearchAgent failed (continuing without search): {type(e).__name__}: {str(e)}")
        elif request.use_search and not search_agent:
            logger.warning("Search requested but SearchAgent not initialized")
        else:
            logger.info("Step 3: Skipping search (use_search=False)")
        
        # Steps 4 and 5: Generate summary and recommendations.
        # Independent Gemini calls, so run them together - sequentially they dominated
        # the request time. /predict is a sync def in FastAPI's threadpool, so this is safe.
        logger.info("Steps 4-5: Generating summary and recommendations...")
        with ThreadPoolExecutor(max_workers=2) as pool:
            summary_future = pool.submit(
                interpreter.summarize,
                forecast_data=forecast_data,
                search_context=search_context
            )
            advice_future = pool.submit(
                recommender.recommend,
                aqi=forecast_data["aqi"],
                profile=request.profile if request.profile else None,
                search_context=search_context,
                pollutants=forecast_data.get("pollutants", {}),
                weather_data={
                    "temp": forecast_data.get("temp"),
                    "humidity": forecast_data.get("humidity"),
                    "wind": forecast_data.get("wind")
                }
            )

            try:
                summary = summary_future.result()
                logger.info(f"Summary generated: {summary[:100]}...")
                # Either provider may have answered; llm.generate picks at call time.
                data_sources.append("AI summary (Gemini/Groq)")
            except Exception as e:
                logger.error(f"Interpreter failed: {type(e).__name__}: {str(e)}")
                # Use fallback summary
                aqi_category = aqi_data.get('category', 'Unknown')
                summary = f"Tomorrow in {request.city}: {forecast_data['temp']}°C, {forecast_data['humidity']}% humidity, AQI {forecast_data['aqi']} ({aqi_category})."
                logger.info(f"Using fallback summary: {summary}")

            try:
                advice = advice_future.result()
                logger.info(f"Advice generated: {advice[:100]}...")
            except Exception as e:
                logger.error(f"Recommender failed: {type(e).__name__}: {str(e)}")
                # Use fallback advice based on AQI
                aqi = forecast_data["aqi"]
                if aqi <= 50:
                    advice = "Air quality is good. Enjoy outdoor activities!"
                elif aqi <= 100:
                    advice = "Air quality is moderate. Sensitive individuals should consider limiting prolonged outdoor activities."
                elif aqi <= 150:
                    advice = "Air quality is unhealthy for sensitive groups. Consider reducing outdoor activities if you have respiratory conditions."
                elif aqi <= 200:
                    advice = "Air quality is unhealthy. Everyone should reduce prolonged outdoor exertion."
                else:
                    advice = "Air quality is very unhealthy or hazardous. Avoid outdoor activities and stay indoors."
                logger.info(f"Using fallback advice: {advice}")

        # Process today's data if available
        today_forecast = None
        today_aqi_data = None
        if today_data:
            try:
                today_aqi_data = predictor.predict(today_data, request.city)
                today_forecast = {
                    "temp": today_data.get("temp"),
                    "humidity": today_data.get("humidity"),
                    "wind": today_data.get("wind"),
                    "aqi": today_aqi_data.get("aqi"),
                    "pollutants": today_aqi_data.get("pollutants", {}),
                    "dominant_pollutant": today_aqi_data.get("dominant_pollutant"),
                    "us_aqi": today_aqi_data.get("us_aqi"),
                    "eu_aqi": today_aqi_data.get("eu_aqi")
                }
            except Exception as e:
                logger.warning(f"Failed to process today's data: {e}")
        
        # Generate hourly predictions for next 24 hours
        logger.info("Generating hourly predictions for next 24 hours...")
        hourly_forecast = []
        try:
            hourly_forecast = predictor.predict_hourly(
                base_weather_data=weather_data,
                city=request.city,
                hours=24
            )
            logger.info(f"Generated {len(hourly_forecast)} hourly predictions")
        except Exception as e:
            logger.warning(f"Failed to generate hourly predictions: {e}")
        
        # Build response with all data
        response_data = {
            "city": request.city,
            "forecast": forecast_data,  # Tomorrow's forecast (main)
            "today_forecast": today_forecast,  # Today's forecast (additional)
            "hourly_forecast": hourly_forecast,  # 24-hour predictions
            "summary": summary,
            "advice": advice,
            "search_results": search_results_data,
            "data_sources": data_sources
        }
        
        logger.info(f"Prediction completed successfully for {request.city}")
        return JSONResponse(content=response_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in /predict: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred. Please try again later. Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
