import requests
import json
from typing import Dict, List, Optional, Any


class WeatherClient:
    """Weather API client implementation."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize the weather client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (default: https://api.weather.example.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle HTTP errors based on status code."""
        if response.status_code == 400:
            raise ValueError("Bad request: Invalid parameters")
        elif response.status_code == 401:
            raise PermissionError("Invalid API key")
        elif response.status_code == 404:
            raise ValueError("City not found")
        elif response.status_code == 429:
            raise RuntimeError("Rate limited - too many requests")
        elif not response.ok:
            raise RuntimeError(f"HTTP error {response.status_code}: {response.text}")
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary containing current weather data
            
        Raises:
            ValueError: If city is not found or request is invalid
            PermissionError: If API key is invalid
            RuntimeError: If rate limited or other HTTP error
        """
        url = f"{self.base_url}/current"
        params = {"city": city}
        
        try:
            response = self.session.get(url, params=params)
            self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}")
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days to forecast
            
        Returns:
            Dictionary containing forecast data
            
        Raises:
            ValueError: If city is not found or request is invalid
            PermissionError: If API key is invalid
            RuntimeError: If rate limited or other HTTP error
        """
        url = f"{self.base_url}/forecast"
        params = {"city": city, "days": days}
        
        try:
            response = self.session.get(url, params=params)
            self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}")
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts for a city.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alerts
            
        Returns:
            Dictionary containing alert subscription data
            
        Raises:
            ValueError: If city is not found or request is invalid
            PermissionError: If API key is invalid
            RuntimeError: If rate limited or other HTTP error
        """
        url = f"{self.base_url}/alert"
        data = {
            "city": city,
            "threshold_temp_c": threshold,
            "callback_url": callback_url
        }
        
        try:
            response = self.session.post(url, json=data)
            self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}")