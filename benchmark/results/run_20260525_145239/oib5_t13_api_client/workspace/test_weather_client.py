import unittest
from unittest.mock import Mock, patch
from weather_client import WeatherClient


class TestWeatherClient(unittest.TestCase):
    def setUp(self):
        self.client = WeatherClient(api_key="test_key")
        self.mock_response = Mock()
        self.mock_response.json.return_value = {}

    def test_get_current_success(self):
        """Test successful current weather request."""
        expected_data = {
            "city": "Beijing",
            "temp_c": 22.5,
            "humidity": 65,
            "condition": "Sunny"
        }
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = expected_data

        with patch.object(self.client.session, 'get', return_value=self.mock_response) as mock_get:
            result = self.client.get_current("Beijing")
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/current",
                params={"city": "Beijing"}
            )
            self.assertEqual(result, expected_data)

    def test_get_forecast_success(self):
        """Test successful forecast request."""
        expected_data = {
            "city": "Beijing",
            "days": 3,
            "forecast": [
                {"date": "2024-03-16", "high": 25, "low": 12, "condition": "Sunny"},
                {"date": "2024-03-17", "high": 20, "low": 10, "condition": "Cloudy"}
            ]
        }
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = expected_data

        with patch.object(self.client.session, 'get', return_value=self.mock_response) as mock_get:
            result = self.client.get_forecast("Beijing", 3)
            mock_get.assert_called_once_with(
                "https://api.weather.example.com/v1/forecast",
                params={"city": "Beijing", "days": 3}
            )
            self.assertEqual(result, expected_data)

    def test_subscribe_alert_success(self):
        """Test successful alert subscription."""
        expected_data = {"alert_id": "a123", "status": "active"}
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = expected_data

        with patch.object(self.client.session, 'post', return_value=self.mock_response) as mock_post:
            result = self.client.subscribe_alert("Beijing", 35, "https://example.com/hook")
            mock_post.assert_called_once_with(
                "https://api.weather.example.com/v1/alert",
                json={
                    "city": "Beijing",
                    "threshold_temp_c": 35,
                    "callback_url": "https://example.com/hook"
                }
            )
            self.assertEqual(result, expected_data)

    def test_error_400(self):
        """Test 400 Bad Request error handling."""
        self.mock_response.status_code = 400
        with patch.object(self.client.session, 'get', return_value=self.mock_response):
            with self.assertRaises(ValueError) as cm:
                self.client.get_current("InvalidCity")
            self.assertEqual(str(cm.exception), "Bad request: invalid parameters")

    def test_error_401(self):
        """Test 401 Invalid API Key error handling."""
        self.mock_response.status_code = 401
        with patch.object(self.client.session, 'get', return_value=self.mock_response):
            with self.assertRaises(PermissionError) as cm:
                self.client.get_current("Beijing")
            self.assertEqual(str(cm.exception), "Invalid API key")

    def test_error_404(self):
        """Test 404 City Not Found error handling."""
        self.mock_response.status_code = 404
        with patch.object(self.client.session, 'get', return_value=self.mock_response):
            with self.assertRaises(LookupError) as cm:
                self.client.get_current("NonexistentCity")
            self.assertEqual(str(cm.exception), "City not found")

    def test_error_429(self):
        """Test 429 Rate Limited error handling."""
        self.mock_response.status_code = 429
        with patch.object(self.client.session, 'get', return_value=self.mock_response):
            with self.assertRaises(RuntimeError) as cm:
                self.client.get_current("Beijing")
            self.assertEqual(str(cm.exception), "Rate limited")


if __name__ == '__main__':
    unittest.main()
