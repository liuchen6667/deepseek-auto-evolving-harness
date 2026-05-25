import requests
import json
from typing import Dict, List, Optional, Any


class WeatherClient:
    """
    Client for Weather API.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.example.com/v1"):
        """
        Initialize WeatherClient.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (defaults to production URL)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            Dict containing response data
            
        Raises:
            ValueError: For client errors (400, 401, 404)
            RuntimeError: For rate limiting (429) or other server errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=self.headers,
                timeout=10
            )
            
            # Handle error responses
            if response.status_code == 400:
                raise ValueError("Bad request: Invalid parameters")
            elif response.status_code == 401:
                raise ValueError("Invalid API key")
            elif response.status_code == 404:
                raise ValueError("City not found")
            elif response.status_code == 429:
                raise RuntimeError("Rate limited. Please try again later.")
            elif response.status_code >= 500:
                raise RuntimeError(f"Server error: {response.status_code}")
            
            # Parse successful response
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as e:
                # Handle cases where response.json() raises ValueError (e.g., invalid JSON)
                raise RuntimeError(f"Invalid response format: {str(e)}") from e
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {str(e)}") from e
    
    def get_current(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dict containing current weather data
            
        Example:
            {"city": "Beijing", "temp_c": 22.5, "humidity": 65, "condition": "Sunny"}
        """
        params = {"city": city}
        return self._make_request("GET", "/current", params=params)
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days for forecast (1-7)
            
        Returns:
            Dict containing forecast data
            
        Example:
            {
                "city": "Beijing", 
                "days": 3, 
                "forecast": [
                    {"date": "2024-03-16", "high": 25, "low": 12, "condition": "Sunny"},
                    ...
                ]
            }
        """
        params = {"city": city, "days": days}
        return self._make_request("GET", "/forecast", params=params)
    
    def subscribe_alert(self, city: str, threshold: float, callback_url: str) -> Dict[str, Any]:
        """
        Subscribe to weather alerts for a city.
        
        Args:
            city: City name
            threshold: Temperature threshold in Celsius
            callback_url: URL to receive alerts
            
        Returns:
            Dict containing alert subscription details
            
        Example:
            {"alert_id": "a123", "status": "active"}
        """
        data = {
            "city": city,
            "threshold_temp_c": threshold,
            "callback_url": callback_url
        }
        return self._make_request("POST", "/alert", data=data)
