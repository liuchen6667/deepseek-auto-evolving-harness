import requests
import json
from typing import Dict, List, Optional, Any


class WeatherAPIError(Exception):
    """Base exception for Weather API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WeatherClient:
    """Client for Weather API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """Initialize the Weather API client.
        
        Args:
            api_key: Your API key
            base_url: Base URL for the API (default: https://api.weather.example.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API and handle errors."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
        
        # Handle error responses
        if response.status_code == 400:
            raise WeatherAPIError("Bad request: Invalid parameters", 400)
        elif response.status_code == 401:
            raise WeatherAPIError("Invalid API key", 401)
        elif response.status_code == 404:
            raise WeatherAPIError("City not found", 404)
        elif response.status_code == 429:
            raise WeatherAPIError("Rate limited. Please try again later", 429)
        elif response.status_code >= 500:
            raise WeatherAPIError(f"Server error: {response.status_code}", response.status_code)
        
        # Try to parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            raise WeatherAPIError(f"Invalid JSON response: {response.text[:200]}")
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather data
            
        Raises:
            WeatherAPIError: If the request fails
        """
        endpoint = f"/current?city={city}"
        return self._make_request("GET", endpoint)
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days to forecast (1-7)
            
        Returns:
            Dictionary with forecast data
            
        Raises:
            WeatherAPIError: If the request fails
        """
        endpoint = f"/forecast?city={city}&days={days}"
        return self._make_request("GET", endpoint)
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """Subscribe to weather alerts for a city.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alert callbacks
            
        Returns:
            Dictionary with alert subscription data
            
        Raises:
            WeatherAPIError: If the request fails
        """
        endpoint = "/alert"
        payload = {
            "city": city,
            "threshold_temp_c": threshold,
            "callback_url": callback_url
        }
        return self._make_request("POST", endpoint, json=payload)
