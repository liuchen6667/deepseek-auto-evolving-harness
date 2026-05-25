import requests
import json
from typing import Dict, Any, Optional, List


class WeatherAPIError(Exception):
    """Base exception for Weather API errors"""
    pass


class WeatherAPIClient:
    """Client for Weather API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize the Weather API client.
        
        Args:
            api_key: Your API key for authentication
            base_url: Base URL for the API (default: https://api.weather.example.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise WeatherAPIError(f"Bad request: {response.text}")
        elif response.status_code == 401:
            raise WeatherAPIError("Invalid API key")
        elif response.status_code == 404:
            raise WeatherAPIError("City not found")
        elif response.status_code == 429:
            raise WeatherAPIError("Rate limited")
        else:
            raise WeatherAPIError(f"API error {response.status_code}: {response.text}")
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dict containing current weather data
            
        Raises:
            WeatherAPIError: If API returns an error
        """
        url = f"{self.base_url}/current"
        params = {'city': city}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {e}")
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days to forecast
            
        Returns:
            Dict containing forecast data
            
        Raises:
            WeatherAPIError: If API returns an error
        """
        url = f"{self.base_url}/forecast"
        params = {'city': city, 'days': days}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {e}")
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alerts
            
        Returns:
            Dict containing alert subscription details
            
        Raises:
            WeatherAPIError: If API returns an error
        """
        url = f"{self.base_url}/alert"
        data = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        
        try:
            response = self.session.post(url, json=data)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {e}")
