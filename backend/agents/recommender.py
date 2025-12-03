"""
Recommender Agent - Provides personalized health and activity advice based on AQI
"""
import time
from typing import Dict, Optional
import google.generativeai as genai


class RecommenderAgent:
    """
    Agent responsible for providing personalized health and activity recommendations.
    Uses Google Gemini API for generating contextual advice based on AQI and user profile.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the Recommender agent.
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        genai.configure(api_key=gemini_api_key)
        # Try multiple model names in order of preference
        model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✓ Using Gemini model: {model_name}")
                break
            except:
                continue
        
        if not self.model:
            self.model = genai.GenerativeModel('gemini-pro')  # Fallback
        
        self.max_retries = 3
        self.base_delay = 1  # seconds
    
    def recommend(self, aqi: int, profile: Optional[str] = None, search_context: Optional[str] = None, pollutants: Optional[Dict] = None, weather_data: Optional[Dict] = None) -> str:
        """
        Generate comprehensive personalized health and activity recommendations.
        
        Args:
            aqi: Air Quality Index value
            profile: Optional user profile (e.g., "asthma, jogging")
            search_context: Optional search results to enhance the advice
            pollutants: Optional dict of pollutant data
            weather_data: Optional dict of weather conditions
        
        Returns:
            Detailed personalized advice string
        """
        # Get AQI category and description
        aqi_category = self._get_aqi_category(aqi)
        aqi_description = self._get_aqi_description(aqi)
        
        # Build comprehensive prompt
        prompt = f"""Generate detailed, personalized health and activity recommendations based on the following air quality and weather data:

AIR QUALITY:
- AQI: {aqi} ({aqi_category})
- Description: {aqi_description}"""
        
        # Add pollutant details if available
        if pollutants:
            prompt += "\n\nPOLLUTANT LEVELS:"
            for name, data in pollutants.items():
                prompt += f"\n- {name}: {data['value']} {data['unit']} (AQI: {data['aqi']})"
        
        # Add weather details if available
        if weather_data:
            prompt += f"\n\nWEATHER CONDITIONS:"
            if 'temp' in weather_data:
                prompt += f"\n- Temperature: {weather_data['temp']}°C"
            if 'humidity' in weather_data:
                prompt += f"\n- Humidity: {weather_data['humidity']}%"
            if 'wind' in weather_data:
                prompt += f"\n- Wind Speed: {weather_data['wind']} km/h"
        
        # Add user profile if provided
        if profile and profile.strip():
            prompt += f"\n\nUSER PROFILE: {profile}"
            prompt += "\n\nProvide PERSONALIZED recommendations considering their specific health conditions and activities."
        else:
            prompt += "\n\nProvide GENERAL recommendations for the public."
        
        # Add search context if available
        if search_context:
            prompt += f"\n\nRECENT NEWS & ALERTS:\n{search_context}"
        
        prompt += """

INSTRUCTIONS:
1. Provide 4-6 specific, actionable recommendations
2. Address outdoor activities, exercise, and daily routines
3. Include protective measures (masks, air purifiers, timing of activities)
4. Mention vulnerable groups if relevant
5. Explain WHY certain precautions are needed (connect to specific pollutants)
6. If user has health conditions, provide targeted advice
7. Reference weather conditions and how they affect air quality
8. Be supportive and practical, not alarmist
9. Include timing recommendations (best/worst times of day)

Make it comprehensive, scientific, yet easy to understand and follow."""
        
        # Try to get response from Gemini API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                # Extract the advice text
                advice = response.text.strip()
                
                return advice
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.base_delay * (2 ** attempt)
                    print(f"Gemini API call failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    # Final attempt failed, use fallback
                    print(f"Gemini API recommendation failed after {self.max_retries} attempts: {e}. Using fallback template.")
                    return self._fallback_advice_detailed(aqi, profile, pollutants, weather_data)
    
    def _get_aqi_category(self, aqi: int) -> str:
        """
        Get AQI category name from AQI value.
        
        Args:
            aqi: AQI value
        
        Returns:
            Category name string
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
    
    def _get_aqi_description(self, aqi: int) -> str:
        """
        Get detailed AQI description.
        
        Args:
            aqi: AQI value
        
        Returns:
            Description string
        """
        if aqi <= 50:
            return "Air quality is satisfactory, and air pollution poses little or no risk."
        elif aqi <= 100:
            return "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
        elif aqi <= 150:
            return "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        elif aqi <= 200:
            return "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
        elif aqi <= 300:
            return "Health alert: The risk of health effects is increased for everyone."
        else:
            return "Health warning of emergency conditions: everyone is more likely to be affected."
    
    def _fallback_advice_detailed(self, aqi: int, profile: Optional[str] = None, pollutants: Optional[Dict] = None, weather_data: Optional[Dict] = None) -> str:
        """
        Generate detailed template-based advice as fallback.
        
        Args:
            aqi: AQI value
            profile: Optional user profile
            pollutants: Optional pollutant data
            weather_data: Optional weather data
        
        Returns:
            Detailed template-based advice string
        """
        category = self._get_aqi_category(aqi)
        advice_parts = []
        
        # Base advice by AQI category
        if aqi <= 50:
            advice_parts.append("Air quality is excellent. This is an ideal day for all outdoor activities including exercise, sports, and recreation.")
            advice_parts.append("No special precautions needed. Enjoy the fresh air!")
        elif aqi <= 100:
            advice_parts.append("Air quality is acceptable for most people. However, sensitive individuals (children, elderly, those with respiratory conditions) should monitor their symptoms.")
            advice_parts.append("Outdoor activities are generally safe, but consider shorter durations if you're sensitive to air pollution.")
        elif aqi <= 150:
            advice_parts.append("Air quality is unhealthy for sensitive groups. Children, elderly, and people with heart or lung conditions should limit prolonged outdoor exertion.")
            advice_parts.append("Consider wearing N95 masks if you must spend extended time outdoors. Keep windows closed during peak pollution hours.")
        elif aqi <= 200:
            advice_parts.append("Air quality is unhealthy for everyone. Reduce prolonged or heavy outdoor exertion. Everyone should limit time outdoors.")
            advice_parts.append("Wear N95 masks outdoors. Use air purifiers indoors. Avoid outdoor exercise - opt for indoor alternatives.")
        elif aqi <= 300:
            advice_parts.append("Health alert: Air quality is very unhealthy. Everyone should avoid outdoor activities. Stay indoors with windows and doors closed.")
            advice_parts.append("Use air purifiers. Wear N95 masks if you must go outside. Monitor health symptoms closely.")
        else:
            advice_parts.append("Health emergency: Air quality is hazardous. Everyone should remain indoors. Avoid all outdoor activities.")
            advice_parts.append("Seal windows and doors. Use air purifiers on high settings. Seek medical attention if experiencing symptoms.")
        
        # Add pollutant-specific advice
        if pollutants:
            dominant = max(pollutants.items(), key=lambda x: x[1]['aqi'])
            pollutant_name = dominant[0]
            
            if pollutant_name == "PM2.5" or pollutant_name == "PM10":
                advice_parts.append(f"Particulate matter ({pollutant_name}) is the primary concern. These fine particles can penetrate deep into lungs. N95 masks are effective protection.")
            elif pollutant_name == "O3":
                advice_parts.append("Ozone is the primary concern. It's typically highest in afternoon. Plan outdoor activities for morning or evening if possible.")
            elif pollutant_name == "NO2":
                advice_parts.append("Nitrogen dioxide levels are elevated, often from vehicle emissions. Avoid busy roads and traffic areas.")
        
        # Add profile-specific advice
        if profile and profile.strip():
            profile_lower = profile.lower()
            
            if any(condition in profile_lower for condition in ["asthma", "respiratory", "copd", "breathing", "lung"]):
                if aqi > 100:
                    advice_parts.append("⚠️ IMPORTANT for respiratory conditions: Keep rescue inhalers accessible. Monitor symptoms closely. Consider consulting your doctor if symptoms worsen.")
                else:
                    advice_parts.append("For your respiratory condition: Have your medication available and monitor any changes in breathing.")
            
            if any(activity in profile_lower for condition in ["jogging", "running", "exercise", "cycling", "workout"]):
                if aqi > 150:
                    advice_parts.append("Exercise recommendation: Switch to indoor workouts. Gyms, home exercises, or indoor sports are safer alternatives.")
                elif aqi > 100:
                    advice_parts.append("Exercise recommendation: Reduce intensity and duration of outdoor workouts. Consider indoor alternatives.")
                elif aqi > 50:
                    advice_parts.append("Exercise recommendation: You can exercise outdoors, but avoid peak traffic hours and consider slightly shorter sessions.")
            
            if any(group in profile_lower for group in ["elderly", "senior", "old", "child", "children", "kid", "baby", "infant"]):
                advice_parts.append("Extra precautions for vulnerable groups: Limit outdoor exposure more strictly than general population. Monitor health closely.")
        
        # Add weather-related advice
        if weather_data:
            wind = weather_data.get('wind', 0)
            humidity = weather_data.get('humidity', 0)
            
            if wind < 5:
                advice_parts.append("Low wind speeds mean pollutants are not dispersing well. Air quality may be worse in the morning and evening.")
            if humidity > 70:
                advice_parts.append("High humidity can make air quality feel worse and may increase respiratory irritation.")
        
        return " ".join(advice_parts)
    
    def _fallback_advice(self, aqi: int, profile: Optional[str] = None) -> str:
        """
        Generate template-based advice as fallback.
        
        Args:
            aqi: AQI value
            profile: Optional user profile
        
        Returns:
            Template-based advice string
        """
        category = self._get_aqi_category(aqi)
        
        # Base advice by AQI category
        if aqi <= 50:
            base_advice = "Air quality is good. It's a great day for outdoor activities."
        elif aqi <= 100:
            base_advice = "Air quality is moderate. Most people can enjoy outdoor activities, but sensitive individuals should consider limiting prolonged outdoor exertion."
        elif aqi <= 150:
            base_advice = "Air quality is unhealthy for sensitive groups. If you have respiratory conditions, consider reducing prolonged outdoor activities."
        elif aqi <= 200:
            base_advice = "Air quality is unhealthy. Everyone should reduce prolonged outdoor exertion. Consider indoor activities instead."
        elif aqi <= 300:
            base_advice = "Air quality is very unhealthy. Avoid outdoor activities. Keep windows closed and use air purifiers if available."
        else:
            base_advice = "Air quality is hazardous. Stay indoors with windows closed. Avoid all outdoor activities."
        
        # Add profile-specific advice if provided
        if profile and profile.strip():
            profile_lower = profile.lower()
            
            if any(condition in profile_lower for condition in ["asthma", "respiratory", "copd", "breathing"]):
                if aqi > 100:
                    base_advice += " Given your respiratory condition, keep your medication handy and monitor symptoms closely."
                else:
                    base_advice += " Monitor your symptoms and have your medication available."
            
            if any(activity in profile_lower for activity in ["jogging", "running", "exercise", "cycling"]):
                if aqi > 100:
                    base_advice += " Consider indoor exercise alternatives."
                elif aqi > 50:
                    base_advice += " You can exercise outdoors, but consider shorter or less intense sessions."
        
        return base_advice
