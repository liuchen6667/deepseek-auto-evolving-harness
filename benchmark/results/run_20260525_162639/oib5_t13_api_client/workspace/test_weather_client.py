import unittest
from unittest.mock import Mock, patch
import weather_client


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_123"
        self.client = weather_client.WeatherClient(self.api_key)
    
    def test_init(self):
        """Test client initialization."""
        client = weather_client.WeatherClient("my_key", "https://custom.url/v1")
        self.assertEqual(client.api_key, "my_key")
        self.assertEqual(client.base_url, "https://custom.url/v1")
        self.assertEqual(client.session.headers["X-API-Key"], "my_key")
        self.assertEqual(client.session.headers["Content-Type"], "application/json")
    
    @patch('weather_client.requests.Session')
    def test_get_current_success(self, mock_session_class):
        """Test successful get_current request."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": "Beijing",
            "temp_c": 22.5,
            "humidity": 65,
            "condition": "Sunny"
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute
        result = client.get_current("Beijing")
        
        # Verify
        mock_session.get.assert_called_once_with(
            "https://api.weather.example.com/v1/current",
            params={"city": "Beijing"}
        )
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["temp_c"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
    
    @patch('weather_client.requests.Session')
    def test_get_forecast_success(self, mock_session_class):
        """Test successful get_forecast request."""
        # Setup mock
        mock_session = Mock()
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
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute
        result = client.get_forecast("Beijing", 3)
        
        # Verify
        mock_session.get.assert_called_once_with(
            "https://api.weather.example.com/v1/forecast",
            params={"city": "Beijing", "days": 3}
        )
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["days"], 3)
        self.assertEqual(len(result["forecast"]), 2)
        self.assertEqual(result["forecast"][0]["high"], 25)
    
    @patch('weather_client.requests.Session')
    def test_subscribe_alert_success(self, mock_session_class):
        """Test successful subscribe_alert request."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alert_id": "a123",
            "status": "active"
        }
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute
        result = client.subscribe_alert("Beijing", 35.0, "https://example.com/hook")
        
        # Verify
        mock_session.post.assert_called_once_with(
            "https://api.weather.example.com/v1/alert",
            json={
                "city": "Beijing",
                "threshold_temp_c": 35.0,
                "callback_url": "https://example.com/hook"
            }
        )
        self.assertEqual(result["alert_id"], "a123")
        self.assertEqual(result["status"], "active")
    
    @patch('weather_client.requests.Session')
    def test_get_current_city_not_found(self, mock_session_class):
        """Test get_current with 404 error (city not found)."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = "City not found"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute and verify exception
        with self.assertRaises(ValueError) as context:
            client.get_current("UnknownCity")
        
        self.assertEqual(str(context.exception), "City not found")
        mock_session.get.assert_called_once()
    
    @patch('weather_client.requests.Session')
    def test_get_forecast_invalid_api_key(self, mock_session_class):
        """Test get_forecast with 401 error (invalid API key)."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.ok = False
        mock_response.text = "Invalid API key"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute and verify exception
        with self.assertRaises(PermissionError) as context:
            client.get_forecast("Beijing", 3)
        
        self.assertEqual(str(context.exception), "Invalid API key")
        mock_session.get.assert_called_once()
    
    @patch('weather_client.requests.Session')
    def test_subscribe_alert_rate_limited(self, mock_session_class):
        """Test subscribe_alert with 429 error (rate limited)."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.ok = False
        mock_response.text = "Too many requests"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute and verify exception
        with self.assertRaises(RuntimeError) as context:
            client.subscribe_alert("Beijing", 35.0, "https://example.com/hook")
        
        self.assertEqual(str(context.exception), "Rate limited - too many requests")
        mock_session.post.assert_called_once()
    
    @patch('weather_client.requests.Session')
    def test_get_current_bad_request(self, mock_session_class):
        """Test get_current with 400 error (bad request)."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.ok = False
        mock_response.text = "Missing city parameter"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute and verify exception
        with self.assertRaises(ValueError) as context:
            client.get_current("")
        
        self.assertEqual(str(context.exception), "Bad request: Invalid parameters")
        mock_session.get.assert_called_once()
    
    @patch('weather_client.requests.Session')
    def test_network_error(self, mock_session_class):
        """Test network error handling."""
        # Setup mock to raise RequestException
        mock_session = Mock()
        mock_session.get.side_effect = weather_client.requests.exceptions.RequestException("Connection failed")
        mock_session_class.return_value = mock_session
        
        # Create client with mocked session
        client = weather_client.WeatherClient(self.api_key)
        client.session = mock_session
        
        # Execute and verify exception
        with self.assertRaises(RuntimeError) as context:
            client.get_current("Beijing")
        
        self.assertIn("Network error", str(context.exception))
        mock_session.get.assert_called_once()


if __name__ == '__main__':
    unittest.main()