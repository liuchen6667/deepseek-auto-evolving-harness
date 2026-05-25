import requests
import json


class WeatherClient:
    """
    Client for Weather API.
    """
    
    def __init__(self, api_key, base_url="https://api.weather.example.com/v1"):
        """
        Initialize the WeatherClient.
        
        Args:
            api_key (str): API key for authentication
            base_url (str): Base URL of the API, defaults to the spec URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
    
    def _handle_response(self, response):
        """
        Handle API response and raise appropriate exceptions for errors.
        
        Args:
            response: requests.Response object
        
        Returns:
            dict: JSON response data
        
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API Key
            LookupError: For 404 City Not Found
            RuntimeError: For 429 Rate Limited
            requests.exceptions.HTTPError: For other HTTP errors
        """
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise ValueError("Bad request: " + response.text)
        elif response.status_code == 401:
            raise PermissionError("Invalid API key")
        elif response.status_code == 404:
            raise LookupError("City not found")
        elif response.status_code == 429:
            raise RuntimeError("Rate limited")
        else:
            response.raise_for_status()
    
    def get_current(self, city):
        """
        Get current weather for a city.
        
        Args:
            city (str): City name
        
        Returns:
            dict: Current weather data with keys: city, temp_c, humidity, condition
        
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API Key
            LookupError: For 404 City Not Found
            RuntimeError: For 429 Rate Limited
            requests.exceptions.RequestException: For network errors
        """
        url = f"{self.base_url}/current"
        params = {"city": city}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except (ValueError, PermissionError, LookupError, RuntimeError):
            # Re-raise the specific exceptions
            raise
        except requests.exceptions.RequestException as e:
            # Wrap network errors
            raise requests.exceptions.RequestException(f"Network error: {str(e)}")
    
    def get_forecast(self, city, days):
        """
        Get weather forecast for a city for N days.
        
        Args:
            city (str): City name
            days (int): Number of days for forecast
        
        Returns:
            dict: Forecast data with keys: city, days, forecast (list of day objects)
        
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API Key
            LookupError: For 404 City Not Found
            RuntimeError: For 429 Rate Limited
            requests.exceptions.RequestException: For network errors
        """
        url = f"{self.base_url}/forecast"
        params = {"city": city, "days": days}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except (ValueError, PermissionError, LookupError, RuntimeError):
            # Re-raise the specific exceptions
            raise
        except requests.exceptions.RequestException as e:
            # Wrap network errors
            raise requests.exceptions.RequestException(f"Network error: {str(e)}")
    
    def subscribe_alert(self, city, threshold, callback_url):
        """
        Subscribe to weather alerts for a city.
        
        Args:
            city (str): City name
            threshold (float): Temperature threshold in Celsius
            callback_url (str): URL to receive alerts
        
        Returns:
            dict: Alert subscription data with keys: alert_id, status
        
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API Key
            LookupError: For 404 City Not Found
            RuntimeError: For 429 Rate Limited
            requests.exceptions.RequestException: For network errors
        """
        url = f"{self.base_url}/alert"
        data = {
            "city": city,
            "threshold_temp_c": threshold,
            "callback_url": callback_url
        }
        
        try:
            response = self.session.post(url, json=data)
            return self._handle_response(response)
        except (ValueError, PermissionError, LookupError, RuntimeError):
            # Re-raise the specific exceptions
            raise
        except requests.exceptions.RequestException as e:
            # Wrap network errors
            raise requests.exceptions.RequestException(f"Network error: {str(e)}")
