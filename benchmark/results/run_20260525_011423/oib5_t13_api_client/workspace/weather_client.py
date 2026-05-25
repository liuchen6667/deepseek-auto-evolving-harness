import requests
import json
from typing import Dict, List, Optional, Union


class WeatherClient:
    """Weather API client based on the specification in api_spec.md"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """Initialize the weather client.
        
        Args:
            api_key: Your API key for authentication
            base_url: Base URL for the API (defaults to spec base URL)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle API errors based on status code."""
        if response.status_code == 400:
            raise ValueError(f"Bad request: {response.text}")
        elif response.status_code == 401:
            raise PermissionError(f"Invalid API key: {response.text}")
        elif response.status_code == 404:
            raise FileNotFoundError(f"City not found: {response.text}")
        elif response.status_code == 429:
            raise RuntimeError(f"Rate limited: {response.text}")
        elif response.status_code >= 400:
            raise Exception(f"API error {response.status_code}: {response.text}")
    
    def get_current(self, city: str) -> Dict[str, Union[str, float, int]]:
        """Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather data
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/current"
        params = {'city': city}
        
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            self._handle_error(response)
        
        return response.json()
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Union[str, int, List[Dict]]]:
        """Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days to forecast (1-7)
            
        Returns:
            Dictionary with forecast data
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/forecast"
        params = {'city': city, 'days': days}
        
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            self._handle_error(response)
        
        return response.json()
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, str]:
        """Subscribe to weather alerts.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alerts
            
        Returns:
            Dictionary with alert subscription info
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/alert"
        data = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        
        response = self.session.post(url, json=data)
        if response.status_code != 200:
            self._handle_error(response)
        
        return response.json()
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
