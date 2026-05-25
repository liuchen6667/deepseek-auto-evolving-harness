import requests
import json


class WeatherClient:
    """
    Client for Weather API
    """
    
    def __init__(self, api_key, base_url="https://api.weather.example.com/v1"):
        """
        Initialize the WeatherClient
        
        Args:
            api_key (str): API key for authentication
            base_url (str): Base URL for the API (default: https://api.weather.example.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Internal method to make HTTP requests with error handling
        
        Args:
            method (str): HTTP method ('GET', 'POST', etc.)
            endpoint (str): API endpoint path
            params (dict): Query parameters
            data (dict): Request body data
            
        Returns:
            dict: Response JSON data
            
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API key
            LookupError: For 404 City not found
            ConnectionError: For 429 Rate limited
            Exception: For other HTTP errors
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, params=params, 
                                       json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle specific error codes
            if response.status_code == 400:
                raise ValueError(f"Bad request: {response.text}")
            elif response.status_code == 401:
                raise PermissionError(f"Invalid API key: {response.text}")
            elif response.status_code == 404:
                raise LookupError(f"City not found: {response.text}")
            elif response.status_code == 429:
                raise ConnectionError(f"Rate limited: {response.text}")
            elif response.status_code >= 400:
                raise Exception(f"HTTP error {response.status_code}: {response.text}")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise ConnectionError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Connection error")
    
    def get_current(self, city):
        """
        Get current weather for a city
        
        Args:
            city (str): City name
            
        Returns:
            dict: Current weather data
            
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API key
            LookupError: For 404 City not found
            ConnectionError: For 429 Rate limited
        """
        params = {'city': city}
        return self._make_request('GET', 'current', params=params)
    
    def get_forecast(self, city, days):
        """
        Get weather forecast for a city for N days
        
        Args:
            city (str): City name
            days (int): Number of days for forecast
            
        Returns:
            dict: Forecast data
            
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API key
            LookupError: For 404 City not found
            ConnectionError: For 429 Rate limited
        """
        params = {'city': city, 'days': days}
        return self._make_request('GET', 'forecast', params=params)
    
    def subscribe_alert(self, city, threshold, callback_url):
        """
        Subscribe to weather alerts for a city
        
        Args:
            city (str): City name
            threshold (float): Temperature threshold in Celsius
            callback_url (str): Callback URL for alerts
            
        Returns:
            dict: Alert subscription data
            
        Raises:
            ValueError: For 400 Bad Request
            PermissionError: For 401 Invalid API key
            LookupError: For 404 City not found
            ConnectionError: For 429 Rate limited
        """
        data = {
            'city': city,
            'threshold_temp_c': threshold,
            'callback_url': callback_url
        }
        return self._make_request('POST', 'alert', data=data)
