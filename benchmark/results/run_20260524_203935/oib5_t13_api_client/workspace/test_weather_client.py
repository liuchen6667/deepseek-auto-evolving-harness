import unittest
from unittest.mock import Mock, patch
import json
import sys
import requests
from weather_client import WeatherClient, WeatherAPIError


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key-123"
        self.client = WeatherClient(self.api_key)
    
    def test_init(self):
        """Test client initialization"""
        client = WeatherClient(self.api_key, "https://api.test.com/v1")
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.base_url, "https://api.test.com/v1")
        self.assertIn("X-API-Key", client.session.headers)
        self.assertEqual(client.session.headers["X-API-Key"], self.api_key)
    
    @patch('weather_client.requests.Session.request')
    def test_get_current_success(self, mock_request):
        """Test successful current weather request"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": "Beijing",
            "temp_c": 22.5,
            "humidity": 65,
            "condition": "Sunny"
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = self.client.get_current("Beijing")
        
        # Assertions
        mock_request.assert_called_once_with(
            "GET",
            "https://api.weather.example.com/v1/current?city=Beijing"
        )
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["temp_c"], 22.5)
        self.assertEqual(result["humidity"], 65)
        self.assertEqual(result["condition"], "Sunny")
    
    @patch('weather_client.requests.Session.request')
    def test_get_forecast_success(self, mock_request):
        """Test successful forecast request"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": "Beijing",
            "days": 3,
            "forecast": [
                {"date": "2024-03-16", "high": 25, "low": 12, "condition": "Sunny"},
                {"date": "2024-03-17", "high": 20, "low": 10, "condition": "Cloudy"}
            ]
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = self.client.get_forecast("Beijing", 3)
        
        # Assertions
        mock_request.assert_called_once_with(
            "GET",
            "https://api.weather.example.com/v1/forecast?city=Beijing&days=3"
        )
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["days"], 3)
        self.assertEqual(len(result["forecast"]), 2)
        self.assertEqual(result["forecast"][0]["date"], "2024-03-16")
    
    @patch('weather_client.requests.Session.request')
    def test_subscribe_alert_success(self, mock_request):
        """Test successful alert subscription"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alert_id": "a123",
            "status": "active"
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = self.client.subscribe_alert("Beijing", 35.0, "https://example.com/hook")
        
        # Assertions
        expected_payload = {
            "city": "Beijing",
            "threshold_temp_c": 35.0,
            "callback_url": "https://example.com/hook"
        }
        mock_request.assert_called_once_with(
            "POST",
            "https://api.weather.example.com/v1/alert",
            json=expected_payload
        )
        self.assertEqual(result["alert_id"], "a123")
        self.assertEqual(result["status"], "active")
    
    @patch('weather_client.requests.Session.request')
    def test_error_400(self, mock_request):
        """Test 400 Bad Request error"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_request.return_value = mock_response
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("InvalidCity!@#")
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, "Bad request: Invalid parameters")
    
    @patch('weather_client.requests.Session.request')
    def test_error_401(self, mock_request):
        """Test 401 Unauthorized error"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_request.return_value = mock_response
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("Beijing")
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.message, "Invalid API key")
    
    @patch('weather_client.requests.Session.request')
    def test_error_404(self, mock_request):
        """Test 404 Not Found error"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "City not found"
        mock_request.return_value = mock_response
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("UnknownCity")
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.message, "City not found")
    
    @patch('weather_client.requests.Session.request')
    def test_error_429(self, mock_request):
        """Test 429 Rate Limited error"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too many requests"
        mock_request.return_value = mock_response
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("Beijing")
        
        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.message, "Rate limited. Please try again later")
    
    @patch('weather_client.requests.Session.request')
    def test_network_error(self, mock_request):
        """Test network connection error"""
        # Mock network error
        mock_request.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Request failed: Network error", context.exception.message)
        self.assertIsNone(context.exception.status_code)
    
    @patch('weather_client.requests.Session.request')
    def test_invalid_json_response(self, mock_request):
        """Test invalid JSON response handling"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Not JSON"
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_request.return_value = mock_response
        
        # Call method and assert exception
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Invalid JSON response", context.exception.message)


if __name__ == '__main__':
    unittest.main()
