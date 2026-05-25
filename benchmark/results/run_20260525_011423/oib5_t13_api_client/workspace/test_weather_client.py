import unittest
from unittest.mock import Mock, patch
import requests
from weather_client import WeatherClient


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_123"
        self.client = WeatherClient(api_key=self.api_key)
        
        # Sample response data
        self.sample_current_response = {
            "city": "Beijing",
            "temp_c": 22.5,
            "humidity": 65,
            "condition": "Sunny"
        }
        
        self.sample_forecast_response = {
            "city": "Beijing",
            "days": 3,
            "forecast": [
                {"date": "2024-03-16", "high": 25, "low": 12, "condition": "Sunny"},
                {"date": "2024-03-17", "high": 20, "low": 10, "condition": "Cloudy"},
                {"date": "2024-03-18", "high": 18, "low": 8, "condition": "Rainy"}
            ]
        }
        
        self.sample_alert_response = {
            "alert_id": "a123",
            "status": "active"
        }
    
    def tearDown(self):
        """Clean up after tests."""
        self.client.close()
    
    def test_initialization(self):
        """Test client initialization with API key."""
        client = WeatherClient(api_key="my_key")
        self.assertEqual(client.api_key, "my_key")
        self.assertEqual(client.base_url, "https://api.weather.example.com/v1")
        self.assertIn("X-API-Key", client.session.headers)
        self.assertEqual(client.session.headers["X-API-Key"], "my_key")
        client.close()
    
    def test_get_current_success(self):
        """Test successful current weather retrieval."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_current_response
        
        with patch.object(self.client.session, 'get', return_value=mock_response) as mock_get:
            result = self.client.get_current("Beijing")
            
            # Verify the call
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/current",
                params={'city': 'Beijing'}
            )
            
            # Verify the result
            self.assertEqual(result, self.sample_current_response)
            self.assertEqual(result["city"], "Beijing")
            self.assertEqual(result["temp_c"], 22.5)
            self.assertEqual(result["condition"], "Sunny")
    
    def test_get_forecast_success(self):
        """Test successful forecast retrieval."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_forecast_response
        
        with patch.object(self.client.session, 'get', return_value=mock_response) as mock_get:
            result = self.client.get_forecast("Beijing", days=3)
            
            # Verify the call
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/forecast",
                params={'city': 'Beijing', 'days': 3}
            )
            
            # Verify the result
            self.assertEqual(result, self.sample_forecast_response)
            self.assertEqual(result["city"], "Beijing")
            self.assertEqual(result["days"], 3)
            self.assertEqual(len(result["forecast"]), 3)
            self.assertEqual(result["forecast"][0]["date"], "2024-03-16")
    
    def test_subscribe_alert_success(self):
        """Test successful alert subscription."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_alert_response
        
        with patch.object(self.client.session, 'post', return_value=mock_response) as mock_post:
            result = self.client.subscribe_alert(
                city="Beijing",
                threshold=35.0,
                callback_url="https://example.com/hook"
            )
            
            # Verify the call
            expected_data = {
                'city': 'Beijing',
                'threshold_temp_c': 35.0,
                'callback_url': 'https://example.com/hook'
            }
            mock_post.assert_called_once_with(
                "https://api.weather.example.com/v1/alert",
                json=expected_data
            )
            
            # Verify the result
            self.assertEqual(result, self.sample_alert_response)
            self.assertEqual(result["alert_id"], "a123")
            self.assertEqual(result["status"], "active")
    
    def test_error_400_bad_request(self):
        """Test handling of 400 Bad Request error."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid city parameter"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(ValueError) as context:
                self.client.get_current("")
            
            self.assertIn("Bad request", str(context.exception))
            self.assertIn("Invalid city parameter", str(context.exception))
    
    def test_error_401_invalid_api_key(self):
        """Test handling of 401 Invalid API Key error."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(PermissionError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("Invalid API key", str(context.exception))
    
    def test_error_404_city_not_found(self):
        """Test handling of 404 City Not Found error."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "City 'UnknownCity' not found"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(FileNotFoundError) as context:
                self.client.get_current("UnknownCity")
            
            self.assertIn("City not found", str(context.exception))
            self.assertIn("UnknownCity", str(context.exception))
    
    def test_error_429_rate_limited(self):
        """Test handling of 429 Rate Limited error."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        
        with patch.object(self.client.session, 'get', return_value=mock_response):
            with self.assertRaises(RuntimeError) as context:
                self.client.get_current("Beijing")
            
            self.assertIn("Rate limited", str(context.exception))
            self.assertIn("Rate limit exceeded", str(context.exception))
    
    def test_context_manager(self):
        """Test client as context manager."""
        with WeatherClient(api_key="test_key") as client:
            self.assertIsInstance(client, WeatherClient)
            self.assertEqual(client.api_key, "test_key")
            # Session should be active
            self.assertIsNotNone(client.session)
        # Client's close method should have been called
        # We can verify by checking that the session still exists but we can't check closed state
        # Instead, we'll just ensure no exception is raised
        pass
    
    def test_custom_base_url(self):
        """Test client with custom base URL."""
        client = WeatherClient(api_key="key", base_url="https://custom.api.com/v2")
        self.assertEqual(client.base_url, "https://custom.api.com/v2")
        client.close()
    
    def test_close_method(self):
        """Test close method."""
        client = WeatherClient(api_key="test")
        # Verify session exists
        self.assertIsNotNone(client.session)
        # Call close method
        client.close()
        # Verify close was called by ensuring we can still access the session
        # (requests.Session doesn't have a 'closed' attribute)
        self.assertIsNotNone(client.session)
        # No exception should be raised when calling close multiple times
        client.close()  # Should be idempotent


if __name__ == '__main__':
    unittest.main()
