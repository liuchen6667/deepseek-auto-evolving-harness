import unittest
from unittest.mock import patch, Mock
import weather_client
import requests


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient."""
    
    def setUp(self):
        """Set up test client."""
        self.api_key = "test-api-key-123"
        self.base_url = "https://api.weather.example.com/v1"
        self.client = weather_client.WeatherClient(self.api_key, self.base_url)
    
    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertEqual(self.client.headers["X-API-Key"], self.api_key)
        self.assertEqual(self.client.headers["Content-Type"], "application/json")
    
    @patch('weather_client.requests.request')
    def test_get_current_success(self, mock_request):
        """Test successful get_current request."""
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
        
        # Verify request
        mock_request.assert_called_once_with(
            method="GET",
            url=f"{self.base_url}/current",
            params={"city": "Beijing"},
            json=None,
            headers=self.client.headers,
            timeout=10
        )
        
        # Verify result
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["temp_c"], 22.5)
        self.assertEqual(result["humidity"], 65)
        self.assertEqual(result["condition"], "Sunny")
    
    @patch('weather_client.requests.request')
    def test_get_forecast_success(self, mock_request):
        """Test successful get_forecast request."""
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
        
        # Verify request
        mock_request.assert_called_once_with(
            method="GET",
            url=f"{self.base_url}/forecast",
            params={"city": "Beijing", "days": 3},
            json=None,
            headers=self.client.headers,
            timeout=10
        )
        
        # Verify result
        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["days"], 3)
        self.assertEqual(len(result["forecast"]), 2)
        self.assertEqual(result["forecast"][0]["date"], "2024-03-16")
        self.assertEqual(result["forecast"][1]["condition"], "Cloudy")
    
    @patch('weather_client.requests.request')
    def test_subscribe_alert_success(self, mock_request):
        """Test successful subscribe_alert request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alert_id": "a123",
            "status": "active"
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = self.client.subscribe_alert(
            city="Beijing",
            threshold=35.0,
            callback_url="https://example.com/hook"
        )
        
        # Verify request
        mock_request.assert_called_once_with(
            method="POST",
            url=f"{self.base_url}/alert",
            params=None,
            json={
                "city": "Beijing",
                "threshold_temp_c": 35.0,
                "callback_url": "https://example.com/hook"
            },
            headers=self.client.headers,
            timeout=10
        )
        
        # Verify result
        self.assertEqual(result["alert_id"], "a123")
        self.assertEqual(result["status"], "active")
    
    @patch('weather_client.requests.request')
    def test_error_400_bad_request(self, mock_request):
        """Test handling of 400 Bad Request error."""
        # Mock response with 400 status
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Verify error is raised
        with self.assertRaises(ValueError) as context:
            self.client.get_current("InvalidCity123")
        
        self.assertIn("Bad request", str(context.exception))
    
    @patch('weather_client.requests.request')
    def test_error_401_invalid_api_key(self, mock_request):
        """Test handling of 401 Invalid API Key error."""
        # Mock response with 401 status
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Verify error is raised
        with self.assertRaises(ValueError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Invalid API key", str(context.exception))
    
    @patch('weather_client.requests.request')
    def test_error_404_city_not_found(self, mock_request):
        """Test handling of 404 City Not Found error."""
        # Mock response with 404 status
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Verify error is raised
        with self.assertRaises(ValueError) as context:
            self.client.get_current("NonExistentCity")
        
        self.assertIn("City not found", str(context.exception))
    
    @patch('weather_client.requests.request')
    def test_error_429_rate_limited(self, mock_request):
        """Test handling of 429 Rate Limited error."""
        # Mock response with 429 status
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        # Verify error is raised
        with self.assertRaises(RuntimeError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Rate limited", str(context.exception))
    
    @patch('weather_client.requests.request')
    def test_network_error(self, mock_request):
        """Test handling of network errors."""
        # Mock request exception
        mock_request.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Verify error is raised
        with self.assertRaises(RuntimeError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Request failed", str(context.exception))
        self.assertIn("Network error", str(context.exception))
    
    @patch('weather_client.requests.request')
    def test_invalid_json_response(self, mock_request):
        """Test handling of invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Verify error is raised
        with self.assertRaises(RuntimeError) as context:
            self.client.get_current("Beijing")
        
        self.assertIn("Invalid JSON response", str(context.exception))


if __name__ == '__main__':
    unittest.main()
