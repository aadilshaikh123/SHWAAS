"""
SearchAgent - Searches for real-time weather context using Tavily API
"""
import logging
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


class SearchAgent:
    """
    Agent responsible for searching real-time weather news and context.
    Uses Tavily API to provide additional context for weather predictions.
    """
    
    def __init__(self, tavily_api_key: str):
        """
        Initialize the SearchAgent with Tavily API key.
        
        Args:
            tavily_api_key: API key for Tavily search service
        
        Raises:
            ValueError: If API key is missing or invalid
        """
        if not tavily_api_key or not isinstance(tavily_api_key, str):
            raise ValueError("Valid Tavily API key is required")
        
        self.api_key = tavily_api_key
        self.client = None
        
        # Initialize Tavily client
        try:
            from tavily import TavilyClient
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("SearchAgent initialized with Tavily API")
        except ImportError:
            logger.error("tavily-python package not installed")
            raise ImportError("tavily-python package is required. Install with: pip install tavily-python")
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            raise
    
    def _get_region_and_country(self, city: str) -> tuple:
        """
        Determine region and country from city name.
        
        Args:
            city: City name
        
        Returns:
            Tuple of (region, country)
        """
        # Indian cities
        indian_cities = [
            "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata", 
            "pune", "ahmedabad", "jaipur", "surat", "lucknow", "kanpur", "nagpur",
            "indore", "bhopal", "patna", "vadodara", "ghaziabad", "ludhiana"
        ]
        
        city_lower = city.lower()
        
        if any(c in city_lower for c in indian_cities):
            return ("India", "India")
        elif any(c in city_lower for c in ["new york", "los angeles", "chicago", "houston", "san francisco", "seattle", "boston", "miami"]):
            return ("United States", "USA")
        elif any(c in city_lower for c in ["london", "manchester", "birmingham", "liverpool"]):
            return ("United Kingdom", "UK")
        elif any(c in city_lower for c in ["beijing", "shanghai", "guangzhou", "shenzhen"]):
            return ("China", "China")
        elif any(c in city_lower for c in ["tokyo", "osaka", "kyoto"]):
            return ("Japan", "Japan")
        elif any(c in city_lower for c in ["paris", "marseille", "lyon"]):
            return ("France", "France")
        elif any(c in city_lower for c in ["berlin", "munich", "hamburg"]):
            return ("Germany", "Germany")
        elif any(c in city_lower for c in ["sydney", "melbourne", "brisbane"]):
            return ("Australia", "Australia")
        else:
            return ("Global", "Global")
    
    def search_weather_context(self, city: str, date: str = "tomorrow") -> Dict:
        """
        Search for weather news including city-specific, regional, and major environmental news.
        
        Args:
            city: City name to search for
            date: Date context (default: "tomorrow")
        
        Returns:
            Dict with keys:
                - results: List of search result dicts
                - summary: Brief summary of findings
                - sources: List of source URLs
                - relevant: Whether results are relevant
                - verification: Cross-verification data
        """
        # Validate client initialization
        if not self.client:
            logger.error("Tavily client not initialized - returning empty results")
            return self._empty_results()
        
        # Validate input
        if not city or not isinstance(city, str):
            logger.warning(f"Invalid city parameter: {city} - returning empty results")
            return self._empty_results()
        
        try:
            all_results = []
            all_sources = []
            
            # Get region and country for broader search
            region, country = self._get_region_and_country(city)
            
            # Multiple search queries for comprehensive coverage
            queries = [
                # City-specific (2 queries)
                f"{city} weather forecast {date}",
                f"{city} air quality AQI pollution {date}",
                
                # Regional news (2 queries)
                f"{region} air pollution crisis latest news",
                f"{region} weather extreme events climate",
                
                # Major environmental news (2 queries)
                f"{country} pollution protests riots environmental",
                f"{country} air quality emergency health alert"
            ]
            
            for query in queries:
                logger.info(f"Searching Tavily for: {query}")
                
                try:
                    # Call Tavily API with search parameters
                    response = self.client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=2,  # 2 per query = 12 total
                        include_domains=[
                            "weather.com", "accuweather.com", "iqair.com", "airnow.gov",
                            "bbc.com", "cnn.com", "reuters.com", "theguardian.com",
                            "aljazeera.com", "apnews.com", "timesofindia.com", "hindustantimes.com"
                        ],
                        include_answer=True
                    )
                    
                    # Validate response
                    if response and isinstance(response, dict):
                        results = response.get("results", [])
                        all_results.extend(results[:2])
                        
                        # Extract sources
                        for result in results[:2]:
                            url = result.get("url", "")
                            if url and url not in all_sources:
                                all_sources.append(url)
                
                except Exception as e:
                    logger.warning(f"Query '{query}' failed: {e}")
                    continue
            
            # Remove duplicates based on URL
            unique_results = []
            seen_urls = set()
            for result in all_results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    unique_results.append(result)
                    seen_urls.add(url)
            
            if not unique_results:
                logger.info(f"No search results found for {city}")
                return self._empty_results()
            
            # Extract and format results with verification
            return self._format_search_results_enhanced(unique_results, city, all_sources)
            
        except ImportError as e:
            logger.error(f"Tavily package import error: {e} - search feature unavailable")
            return self._empty_results()
        
        except Exception as e:
            logger.error(f"Tavily search failed for '{city}': {type(e).__name__}: {str(e)}")
            logger.info("Continuing without search results - prediction flow not affected")
            return self._empty_results()
    
    def _empty_results(self) -> Dict:
        """
        Return empty results structure for error cases.
        
        Returns:
            Dict with empty results
        """
        return {
            "results": [],
            "summary": "",
            "sources": [],
            "relevant": False
        }
    
    def _format_search_results_enhanced(self, results: List[Dict], city: str, sources: List[str]) -> Dict:
        """
        Format search results with enhanced verification and details.
        
        Args:
            results: List of search results
            city: City name for context
            sources: List of source URLs
        
        Returns:
            Formatted results dict with verification data
        """
        try:
            if not results:
                logger.info(f"No search results found for {city}")
                return self._empty_results()
            
            # Format each result for UI display
            formatted_results = []
            
            for result in results[:8]:  # Limit to top 8 results
                # Extract and clean content
                raw_content = result.get("content", "")
                cleaned_content = self._clean_content(raw_content)
                
                # Extract key information from each result
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": cleaned_content,  # Use cleaned content
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date", "")
                }
                
                # Only include results with meaningful content
                if formatted_result["title"] and formatted_result["url"] and len(cleaned_content) > 30:
                    formatted_results.append(formatted_result)
            
            # Generate comprehensive summary from all results
            summary = self._generate_comprehensive_summary(formatted_results, city)
            
            # Cross-verify information across sources
            verification = self._cross_verify_sources(formatted_results, city)
            
            # Determine if results are relevant
            relevant = len(formatted_results) > 0
            
            logger.info(f"Formatted {len(formatted_results)} search results for {city} with verification")
            
            return {
                "results": formatted_results,
                "summary": summary,
                "sources": sources,
                "relevant": relevant,
                "verification": verification,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            return self._empty_results()
    
    def _format_search_results(self, response: Dict, city: str) -> Dict:
        """
        Format Tavily API response into structured results.
        
        Args:
            response: Raw Tavily API response
            city: City name for context
        
        Returns:
            Formatted results dict with keys:
                - results: List of formatted result dicts
                - summary: Brief summary of findings
                - sources: List of source URLs
                - relevant: Whether results are relevant
        """
        try:
            # Extract results from Tavily response
            raw_results = response.get("results", [])
            
            if not raw_results:
                logger.info(f"No search results found for {city}")
                return self._empty_results()
            
            # Format each result for UI display
            formatted_results = []
            sources = []
            
            for result in raw_results[:5]:  # Limit to top 5 results
                # Extract key information from each result
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                }
                
                # Only include results with meaningful content
                if formatted_result["title"] and formatted_result["url"]:
                    formatted_results.append(formatted_result)
                    sources.append(formatted_result["url"])
            
            # Generate summary from top results
            summary = self._generate_summary(formatted_results, city)
            
            # Determine if results are relevant
            relevant = len(formatted_results) > 0
            
            logger.info(f"Formatted {len(formatted_results)} search results for {city}")
            
            return {
                "results": formatted_results,
                "summary": summary,
                "sources": sources,
                "relevant": relevant
            }
            
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            return self._empty_results()
    
    def _clean_content(self, content: str) -> str:
        """
        Clean and format search result content.
        
        Args:
            content: Raw content string
        
        Returns:
            Cleaned content string
        """
        if not content:
            return ""
        
        # Remove markdown headers (##, ###, etc.)
        import re
        content = re.sub(r'#{1,6}\s+', '', content)
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove navigation elements
        content = re.sub(r'(Recents|Products & Account|Special Forecasts|Maps|Forecast)', '', content)
        
        # Remove repeated patterns
        content = re.sub(r'(\b\w+\b)(\s+\1){2,}', r'\1', content)
        
        # Take only first 200 characters of meaningful content
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        if sentences:
            # Take first 2-3 meaningful sentences
            result = '. '.join(sentences[:2])
            if len(result) > 200:
                result = result[:200] + "..."
            return result
        
        return content[:200] + "..." if len(content) > 200 else content
    
    def _generate_comprehensive_summary(self, results: List[Dict], city: str) -> str:
        """
        Generate a comprehensive summary from multiple search results.
        
        Args:
            results: List of formatted search results
            city: City name
        
        Returns:
            Comprehensive summary string
        """
        if not results:
            return ""
        
        try:
            # Collect key information from all results
            summaries = []
            for result in results[:5]:  # Use top 5 results
                content = result.get("content", "")
                if content:
                    # Clean and extract meaningful content
                    cleaned = self._clean_content(content)
                    if cleaned and len(cleaned) > 30:
                        summaries.append(cleaned)
            
            if summaries:
                # Combine summaries intelligently
                combined = " ".join(summaries[:2])  # Use top 2
                if len(combined) > 300:
                    combined = combined[:300] + "..."
                return combined
            else:
                return f"Found {len(results)} recent weather and air quality reports for {city} from multiple sources"
                
        except Exception as e:
            logger.warning(f"Error generating comprehensive summary: {e}")
            return f"Found {len(results)} weather-related articles for {city}"
    
    def _cross_verify_sources(self, results: List[Dict], city: str) -> Dict:
        """
        Cross-verify information across multiple sources.
        
        Args:
            results: List of formatted search results
            city: City name
        
        Returns:
            Dict with verification data
        """
        try:
            verification = {
                "sources_count": len(results),
                "confidence": "high" if len(results) >= 3 else "medium" if len(results) >= 2 else "low",
                "domains": [],
                "latest_update": None,
                "consensus": []
            }
            
            # Extract domains
            for result in results:
                url = result.get("url", "")
                if url:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        if domain and domain not in verification["domains"]:
                            verification["domains"].append(domain)
                    except:
                        pass
            
            # Find latest update
            dates = [r.get("published_date") for r in results if r.get("published_date")]
            if dates:
                verification["latest_update"] = max(dates)
            
            # Look for consensus keywords
            all_content = " ".join([r.get("content", "") for r in results]).lower()
            
            # Weather conditions consensus
            if "rain" in all_content or "precipitation" in all_content:
                verification["consensus"].append("Precipitation expected")
            if "clear" in all_content or "sunny" in all_content:
                verification["consensus"].append("Clear conditions expected")
            if "wind" in all_content or "windy" in all_content:
                verification["consensus"].append("Windy conditions")
            
            # Air quality consensus
            if "poor air quality" in all_content or "high pollution" in all_content:
                verification["consensus"].append("Poor air quality reported")
            if "good air quality" in all_content or "clean air" in all_content:
                verification["consensus"].append("Good air quality reported")
            
            return verification
            
        except Exception as e:
            logger.warning(f"Error in cross-verification: {e}")
            return {
                "sources_count": len(results),
                "confidence": "low",
                "domains": [],
                "latest_update": None,
                "consensus": []
            }
    
    def _generate_summary(self, results: List[Dict], city: str) -> str:
        """
        Generate a brief summary from search results.
        
        Args:
            results: List of formatted search results
            city: City name
        
        Returns:
            Summary string
        """
        if not results:
            return ""
        
        try:
            # Extract key information from top results
            top_result = results[0]
            title = top_result.get("title", "")
            content = top_result.get("content", "")
            
            # Create a concise summary (limit to ~200 characters)
            if content:
                # Take first sentence or first 200 chars
                summary = content.split('.')[0][:200]
                if len(content.split('.')[0]) > 200:
                    summary += "..."
                return summary
            elif title:
                return title
            else:
                return f"Found {len(results)} recent articles about {city} weather"
                
        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return f"Found {len(results)} weather-related articles for {city}"
