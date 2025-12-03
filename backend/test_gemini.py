"""
Test Gemini API with new Client interface
"""
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test the new Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    try:
        print("Testing Gemini 2.0 API...")
        print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        # Create client
        client = genai.Client(api_key=api_key)
        
        # Test simple generation
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Explain how AI works in a few words"
        )
        
        print("\n✅ Gemini API Test Successful!")
        print(f"\nResponse: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini API Test Failed: {e}")
        return False


if __name__ == "__main__":
    test_gemini_api()
