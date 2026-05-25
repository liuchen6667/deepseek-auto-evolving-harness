import requests
import json
from typing import Optional, Dict, Any, List


class WeatherClient:
    """Weather API client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize the weather client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the weather API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise ValueError(f"Bad request: {response.text}")
        elif response.status_code == 401:
            raise PermissionError(f"Invalid API key: {response.text}")
        elif response.status_code == 404:
            raise FileNotFoundError(f"City not found: {response.text}")
        elif response.status_code == 429:
            raise RuntimeError(f"Rate limited: {response.text}")
        else:
            response.raise_for_status()
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dict with current weather data
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/current"
        params = {'city': city}
        
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days for forecast
            
        Returns:
            Dict with forecast data
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/forecast"
        params = {'city': city, 'days': days}
        
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alerts
            
        Returns:
            Dict with alert subscription info
            
        Raises:
            ValueError: Bad request (400)
            PermissionError: Invalid API key (401)
            FileNotFoundError: City not found (404)
            RuntimeError: Rate limited (429)
        """
        url = f"{self.base_url}/alert"
        payload = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)


if __name__ == "__main__":
    # Example usage
    client = WeatherClient(api_key="test_key")
    
    try:
        # Test current weather
        current = client.get_current("Beijing")
        print(f"Current weather: {current}")
        
        # Test forecast
        forecast = client.get_forecast("Beijing", 3)
        print(f"Forecast: {forecast}")
        
        # Test alert subscription
        alert = client.subscribe_alert("Beijing", 35.0, "https://example.com/hook")
        print(f"Alert subscription: {alert}")
        
    except Exception as e:
        print(f"Error: {e}")