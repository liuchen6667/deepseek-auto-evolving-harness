import unittest
from unittest.mock import Mock, patch
import requests
from weather_client import (
    WeatherClient, 
    BadRequestError, 
    UnauthorizedError, 
    NotFoundError, 
    RateLimitError,
    WeatherAPIError
)


class TestWeatherClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key-123"
        self.client = WeatherClient(self.api_key)
    
    def test_init(self):
        """Test client initialization"""
        client = WeatherClient("my-api-key", "https://custom.example.com")
        self.assertEqual(client.api_key, "my-api-key")
        self.assertEqual(client.base_url, "https://custom.example.com")
        self.assertEqual(client.session.headers['X-API-Key'], "my-api-key")
        self.assertEqual(client.session.headers['Content-Type'], "application/json")
    
    def test_get_current_success(self):
        """Test successful current weather request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": "Beijing",
            "temp_c": 22.5,
            "humidity": 65,
            "condition": "Sunny"
        }
        
        with patch.object(self.client.session, 'get', return_value=mock_response) as mock_get:
            result = self.client.get_current("Beijing")
            
            # Verify the request was made correctly
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/current",
                params={'city': 'Beijing'}
            )
            
            # Verify the response
            self.assertEqual(result["city"], "Beijing")
            self.assertEqual(result["temp_c"], 22.5)
            self.assertEqual(result["humidity"], 65)
            self.assertEqual(result["condition"], "Sunny")
    
    def test_get_forecast_success(self):
        """Test successful forecast request"""
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
        
        with patch.object(self.client.session, 'get', return_value=mock_response) as mock_get:
            result = self.client.get_forecast("Beijing", 3)
            
            # Verify the request was made correctly
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/forecast",
                params={'city': 'Beijing', 'days': 3}
            )
            
            # Verify the response
            self.assertEqual(result["city"], "Beijing")
            self.assertEqual(result["days"], 3)
            self.assertEqual(len(result["forecast"]), 2)
            self.assertEqual(result["forecast"][0]["date"], "2024-03-16")
            self.assertEqual(result["forecast"][1]["condition"], "Cloudy")
    
    def test_subscribe_alert_success(self):
        """Test successful alert subscription"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alert_id": "a123",
            "status": "active"
        }
        
        with patch.object(self.client.session, 'post', return_value=mock_response) as mock_post:
            result = self.client.subscribe_alert(
                city="Beijing",
                threshold=35.0,
                callback_url="https://example.com/hook"
            )
            
            # Verify the request was made correctly
            expected_payload = {
                'city': 'Beijing',
                'threshold_temp_c': 35.0,
                'callback_url': 'https://example.com/hook'
            }
            mock_post.assert_called_once_with(
                "https://api.weather.example.com/v1/alert",
                json=expected_payload
            )
            
            # Verify the response
            self.assertEqual(result["alert_id"], "a123")
            self.assertEqual(result["status"], "active")
    
    def test_error_400_bad_request(self):
        """Test handling of 400 Bad Request error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid city parameter"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(BadRequestError) as context:
                self.client.get_current("InvalidCity")
            
            self.assertIn("Bad request", str(context.exception))
            self.assertIn("Invalid city parameter", str(context.exception))
    
    def test_error_401_unauthorized(self):
        """Test handling of 401 Unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(UnauthorizedError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("Invalid API key", str(context.exception))
    
    def test_error_404_not_found(self):
        """Test handling of 404 Not Found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "City 'UnknownCity' not found"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(NotFoundError) as context:
                self.client.get_current("UnknownCity")
            
            self.assertIn("City not found", str(context.exception))
            self.assertIn("UnknownCity", str(context.exception))
    
    def test_error_429_rate_limit(self):
        """Test handling of 429 Rate Limited error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too many requests"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(RateLimitError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("Rate limited", str(context.exception))
            self.assertIn("Too many requests", str(context.exception))
    
    def test_network_error(self):
        """Test handling of network errors"""
        with patch.object(self.client.session, 'get', side_effect=requests.RequestException("Network error")):
            with self.assertRaises(WeatherAPIError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("Request failed", str(context.exception))
            self.assertIn("Network error", str(context.exception))
    
    def test_other_error_codes(self):
        """Test handling of other non-200 error codes"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(WeatherAPIError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("API error 500", str(context.exception))
            self.assertIn("Internal server error", str(context.exception))


if __name__ == '__main__':
    unittest.main()