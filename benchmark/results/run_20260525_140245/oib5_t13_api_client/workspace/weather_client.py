import requests
import json
from typing import Dict, List, Optional, Any


class WeatherAPIError(Exception):
    """Base exception for Weather API errors"""
    pass


class BadRequestError(WeatherAPIError):
    """400 Bad Request"""
    pass


class UnauthorizedError(WeatherAPIError):
    """401 Unauthorized"""
    pass


class NotFoundError(WeatherAPIError):
    """404 Not Found"""
    pass


class RateLimitError(WeatherAPIError):
    """429 Rate Limited"""
    pass


class WeatherClient:
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize the Weather API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (defaults to the specification URL)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions for error codes.
        
        Args:
            response: The HTTP response object
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            BadRequestError: For 400 status code
            UnauthorizedError: For 401 status code
            NotFoundError: For 404 status code
            RateLimitError: For 429 status code
            WeatherAPIError: For other non-200 status codes
        """
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise BadRequestError(f"Bad request: {response.text}")
        elif response.status_code == 401:
            raise UnauthorizedError(f"Invalid API key: {response.text}")
        elif response.status_code == 404:
            raise NotFoundError(f"City not found: {response.text}")
        elif response.status_code == 429:
            raise RateLimitError(f"Rate limited: {response.text}")
        else:
            raise WeatherAPIError(f"API error {response.status_code}: {response.text}")
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with current weather data
            
        Raises:
            WeatherAPIError: If API request fails
        """
        url = f"{self.base_url}/current"
        params = {'city': city}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except requests.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city for specified number of days.
        
        Args:
            city: City name
            days: Number of days for forecast
            
        Returns:
            Dictionary with forecast data
            
        Raises:
            WeatherAPIError: If API request fails
        """
        url = f"{self.base_url}/forecast"
        params = {'city': city, 'days': days}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except requests.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts for a city.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alert callbacks
            
        Returns:
            Dictionary with alert subscription details
            
        Raises:
            WeatherAPIError: If API request fails
        """
        url = f"{self.base_url}/alert"
        payload = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except requests.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")