import requests
import json


class WeatherClient:
    def __init__(self, api_key, base_url="https://api.weather.example.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def _handle_errors(self, response):
        if response.status_code == 400:
            raise ValueError("Bad request: invalid parameters")
        elif response.status_code == 401:
            raise PermissionError("Invalid API key")
        elif response.status_code == 404:
            raise LookupError("City not found")
        elif response.status_code == 429:
            raise RuntimeError("Rate limited")
        response.raise_for_status()

    def get_current(self, city):
        """Get current weather for a city.
        
        Args:
            city (str): City name
        
        Returns:
            dict: Weather data
        """
        url = f"{self.base_url}/current"
        params = {"city": city}
        response = self.session.get(url, params=params)
        self._handle_errors(response)
        return response.json()

    def get_forecast(self, city, days):
        """Get forecast for a city for N days.
        
        Args:
            city (str): City name
            days (int): Number of forecast days
        
        Returns:
            dict: Forecast data
        """
        url = f"{self.base_url}/forecast"
        params = {"city": city, "days": days}
        response = self.session.get(url, params=params)
        self._handle_errors(response)
        return response.json()

    def subscribe_alert(self, city, threshold, callback_url):
        """Subscribe to weather alerts.
        
        Args:
            city (str): City name
            threshold (float): Temperature threshold in Celsius
            callback_url (str): Webhook URL for alerts
        
        Returns:
            dict: Alert subscription info
        """
        url = f"{self.base_url}/alert"
        payload = {
            "city": city,
            "threshold_temp_c": threshold,
            "callback_url": callback_url
        }
        response = self.session.post(url, json=payload)
        self._handle_errors(response)
        return response.json()
