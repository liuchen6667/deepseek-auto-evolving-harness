import unittest
from unittest.mock import Mock, patch
import json
from weather_client import WeatherClient


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient"""
    
    def setUp(self):
        """Set up test client"""
        self.api_key = "test_api_key"
        self.client = WeatherClient(api_key=self.api_key)
    
    def test_init(self):
        """Test client initialization"""
        client = WeatherClient(api_key="test_key", base_url="https://test.com/v1")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.base_url, "https://test.com/v1")
        self.assertEqual(client.session.headers['X-API-Key'], "test_key")
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_success(self, mock_get):
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
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_current("Beijing")
        
        # Verify
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["temp_c"], 22.5)
        mock_get.assert_called_once_with(
            "https://api.weather.example.com/v1/current",
            params={"city": "Beijing"}
        )
    
    @patch('weather_client.requests.Session.get')
    def test_get_forecast_success(self, mock_get):
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
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_forecast("Beijing", 3)
        
        # Verify
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(len(result["forecast"]), 2)
        mock_get.assert_called_once_with(
            "https://api.weather.example.com/v1/forecast",
            params={"city": "Beijing", "days": 3}
        )
    
    @patch('weather_client.requests.Session.post')
    def test_subscribe_alert_success(self, mock_post):
        """Test successful alert subscription"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alert_id": "a123",
            "status": "active"
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.client.subscribe_alert("Beijing", 35.0, "https://example.com/hook")
        
        # Verify
        self.assertEqual(result["alert_id"], "a123")
        self.assertEqual(result["status"], "active")
        mock_post.assert_called_once_with(
            "https://api.weather.example.com/v1/alert",
            json={
                "city": "Beijing",
                "threshold_temp_c": 35.0,
                "callback_url": "https://example.com/hook"
            }
        )
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_400_error(self, mock_get):
        """Test 400 Bad Request error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid city format"
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.client.get_current("Invalid City")
        
        self.assertIn("Bad request", str(context.exception))
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_401_error(self, mock_get):
        """Test 401 Unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_get.return_value = mock_response
        
        with self.assertRaises(PermissionError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Invalid API key", str(context.exception))
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_404_error(self, mock_get):
        """Test 404 Not Found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "City not found"
        mock_get.return_value = mock_response
        
        with self.assertRaises(FileNotFoundError) as context:
            self.client.get_current("UnknownCity")
        
        self.assertIn("City not found", str(context.exception))
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_429_error(self, mock_get):
        """Test 429 Rate Limited error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too many requests"
        mock_get.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Rate limited", str(context.exception))
    
    @patch('weather_client.requests.Session.get')
    def test_get_forecast_404_error(self, mock_get):
        """Test 404 error for forecast"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "City not found"
        mock_get.return_value = mock_response
        
        with self.assertRaises(FileNotFoundError) as context:
            self.client.get_forecast("UnknownCity", 3)
        
        self.assertIn("City not found", str(context.exception))
    
    @patch('weather_client.requests.Session.post')
    def test_subscribe_alert_400_error(self, mock_post):
        """Test 400 error for alert subscription"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid threshold"
        mock_post.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.client.subscribe_alert("Beijing", -100.0, "invalid_url")
        
        self.assertIn("Bad request", str(context.exception))
    
    def test_handle_response_unknown_error(self):
        """Test handling of unknown error status codes"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        
        with self.assertRaises(Exception) as context:
            self.client._handle_response(mock_response)
        
        self.assertIn("Server error", str(context.exception))


if __name__ == "__main__":
    unittest.main()