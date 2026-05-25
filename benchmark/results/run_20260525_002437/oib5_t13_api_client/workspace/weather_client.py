import requests
import json
from typing import Dict, List, Optional, Any


class WeatherAPIError(Exception):
    """Base exception for Weather API errors"""
    pass


class WeatherAPI:
    """Weather API client class"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize the Weather API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the API (default: https://api.weather.example.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            JSON response as dictionary
            
        Raises:
            WeatherAPIError: If API returns an error status code
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            
            # Handle error status codes
            if response.status_code == 400:
                raise WeatherAPIError("Bad request: Invalid parameters")
            elif response.status_code == 401:
                raise WeatherAPIError("Invalid API key")
            elif response.status_code == 404:
                raise WeatherAPIError("City not found")
            elif response.status_code == 429:
                raise WeatherAPIError("Rate limited. Please try again later")
            elif response.status_code >= 400:
                raise WeatherAPIError(f"API error {response.status_code}: {response.text}")
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                raise WeatherAPIError(f"Invalid JSON response: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise WeatherAPIError(f"Invalid JSON response: {str(e)}")
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with current weather data
            
        Example:
            {
                "city": "Beijing",
                "temp_c": 22.5,
                "humidity": 65,
                "condition": "Sunny"
            }
        """
        params = {'city': city}
        return self._make_request('GET', '/current', params=params)
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days for forecast
            
        Returns:
            Dictionary with forecast data
            
        Example:
            {
                "city": "Beijing",
                "days": 3,
                "forecast": [
                    {"date": "2024-03-16", "high": 25, "low": 12, "condition": "Sunny"},
                    {"date": "2024-03-17", "high": 20, "low": 10, "condition": "Cloudy"}
                ]
            }
        """
        params = {'city': city, 'days': days}
        return self._make_request('GET', '/forecast', params=params)
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alert callbacks
            
        Returns:
            Dictionary with alert subscription info
            
        Example:
            {
                "alert_id": "a123",
                "status": "active"
            }
        """
        data = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        return self._make_request('POST', '/alert', json=data)