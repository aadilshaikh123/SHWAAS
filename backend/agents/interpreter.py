"""
Interpreter Agent - Generates natural language summaries of weather forecasts
"""
import logging
from typing import Dict, Optional

from backend.agents import llm

logger = logging.getLogger(__name__)


class InterpreterAgent:
    """
    Agent responsible for generating natural language summaries of forecast data.
    Uses Google Gemini API for natural language generation.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the Interpreter agent.
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        self.gemini_api_key = gemini_api_key
    
    def summarize(self, forecast_data: Dict, search_context: Optional[str] = None) -> str:
        """
        Generate a comprehensive natural language summary of the forecast with detailed explanations.
        
        Args:
            forecast_data: Dict with keys: temp, humidity, wind, aqi, pollutants, etc.
            search_context: Optional search results to enhance the summary
        
        Returns:
            Detailed natural language summary string
        """
        temp = forecast_data.get("temp", "N/A")
        humidity = forecast_data.get("humidity", "N/A")
        wind = forecast_data.get("wind", "N/A")
        aqi = forecast_data.get("aqi", "N/A")
        pollutants = forecast_data.get("pollutants", {})
        dominant_pollutant = forecast_data.get("dominant_pollutant", "N/A")
        us_aqi = forecast_data.get("us_aqi")
        eu_aqi = forecast_data.get("eu_aqi")
        
        # Determine AQI category
        aqi_category = self._get_aqi_category(aqi)
        
        # Build detailed pollutant information
        pollutant_details = ""
        if pollutants:
            pollutant_list = []
            for name, data in pollutants.items():
                pollutant_list.append(f"{name}: {data['value']} {data['unit']} (AQI: {data['aqi']})")
            pollutant_details = "\n- " + "\n- ".join(pollutant_list)
        
        # Create comprehensive prompt for the LLM
        prompt = f"""Generate a detailed, informative weather and air quality summary for tomorrow. Include scientific explanations and health implications.

WEATHER DATA:
- Temperature: {temp}°C
- Humidity: {humidity}%
- Wind Speed: {wind} km/h

AIR QUALITY DATA:
- Overall AQI: {aqi} ({aqi_category})
- Dominant Pollutant: {dominant_pollutant}
{pollutant_details}"""
        
        if us_aqi:
            prompt += f"\n- US EPA AQI: {us_aqi}"
        if eu_aqi:
            prompt += f"\n- European AQI: {eu_aqi}"
        
        # Add search context if available
        if search_context:
            prompt += f"\n\nRECENT NEWS & CONTEXT:\n{search_context}"
        
        prompt += """

INSTRUCTIONS:
Write 3-4 sentences of plain prose covering what this AQI level means in practical
terms, the dominant pollutant and why it matters, and how the weather conditions are
driving the air quality. Use clear, everyday language.

Output plain text only. No markdown, no headings, no bullet points, no bold, no
asterisks or hash characters. Do not add a preamble - start with the forecast itself."""
        
        try:
            return llm.generate(prompt, self.gemini_api_key)
        except llm.AllProvidersFailed as e:
            logger.warning(f"All LLM providers failed ({e}); using fallback template.")
            return self._fallback_summary_detailed(forecast_data)
    
    def _get_aqi_category(self, aqi: int) -> str:
        """
        Get AQI category name from AQI value.
        
        Args:
            aqi: AQI value
        
        Returns:
            Category name string
        """
        if isinstance(aqi, str) or aqi is None:
            return "Unknown"
        
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
    
    def _fallback_summary_detailed(self, forecast_data: Dict) -> str:
        """
        Generate a detailed template-based summary as fallback.
        
        Args:
            forecast_data: Dict with keys: temp, humidity, wind, aqi, pollutants
        
        Returns:
            Detailed template-based summary string
        """
        temp = forecast_data.get("temp", "N/A")
        humidity = forecast_data.get("humidity", "N/A")
        wind = forecast_data.get("wind", "N/A")
        aqi = forecast_data.get("aqi", "N/A")
        dominant_pollutant = forecast_data.get("dominant_pollutant", "PM2.5")
        aqi_category = self._get_aqi_category(aqi) if isinstance(aqi, int) else "unknown"

        # Round for display - raw sensor floats like 30.866666666666664 read badly.
        temp, humidity, wind = (round(v, 1) if isinstance(v, (int, float)) else v
                                for v in (temp, humidity, wind))

        # Build detailed fallback summary
        summary = f"Tomorrow's forecast shows {temp}°C with {humidity}% humidity and wind speeds of {wind} km/h. "
        summary += f"Air quality is {aqi_category.lower()} with an AQI of {aqi}, primarily driven by {dominant_pollutant}. "
        
        # Add health implications based on AQI
        if isinstance(aqi, int):
            if aqi <= 50:
                summary += "Air quality is satisfactory, and air pollution poses little or no risk. Ideal conditions for outdoor activities."
            elif aqi <= 100:
                summary += "Air quality is acceptable. Sensitive individuals should consider limiting prolonged outdoor exertion."
            elif aqi <= 150:
                summary += "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
            elif aqi <= 200:
                summary += "Everyone may begin to experience health effects. Sensitive groups should avoid outdoor activities."
            else:
                summary += "Health alert: everyone may experience serious health effects. Avoid outdoor activities."
        
        return summary
    
    def _fallback_summary(self, forecast_data: Dict) -> str:
        """
        Generate a simple template-based summary as fallback.
        
        Args:
            forecast_data: Dict with keys: temp, humidity, wind, aqi
        
        Returns:
            Template-based summary string
        """
        temp = forecast_data.get("temp", "N/A")
        aqi = forecast_data.get("aqi", "N/A")
        aqi_category = self._get_aqi_category(aqi) if isinstance(aqi, int) else "unknown"
        
        return f"Tomorrow: {temp}°C with {aqi_category.lower()} air quality (AQI {aqi})."
