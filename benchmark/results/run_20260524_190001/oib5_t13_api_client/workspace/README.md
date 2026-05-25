# Weather API Client

A Python client for the Weather API based on the specification in `api_spec.md`.

## Files

1. **`weather_client.py`** - Main client class with:
   - `WeatherClient` class with `__init__(self, api_key, base_url)` constructor
   - `get_current(city)` method
   - `get_forecast(city, days)` method
   - `subscribe_alert(city, threshold, callback_url)` method
   - Proper error handling for 400, 401, 404, and 429 status codes

2. **`test_weather_client.py`** - Comprehensive test suite with:
   - 11 test cases covering success and error scenarios
   - Mocked HTTP requests using `unittest.mock`
   - Tests for all error conditions (400, 401, 404, 429)

3. **`example_usage.py`** - Example script demonstrating usage

## Usage

```python
from weather_client import WeatherClient

# Initialize client
client = WeatherClient(api_key="your_api_key")

# Get current weather
try:
    current = client.get_current("Beijing")
    print(f"Temperature: {current['temp_c']}°C")
except FileNotFoundError:
    print("City not found")
except ValueError:
    print("Bad request")
except PermissionError:
    print("Invalid API key")
except RuntimeError:
    print("Rate limited")

# Get forecast
forecast = client.get_forecast("Beijing", days=3)

# Subscribe to alerts
alert = client.subscribe_alert(
    city="Beijing",
    threshold=35.0,
    callback_url="https://example.com/webhook"
)
```

## Error Handling

The client raises appropriate Python exceptions for HTTP errors:
- `400 Bad Request` → `ValueError`
- `401 Unauthorized` → `PermissionError`
- `404 Not Found` → `FileNotFoundError`
- `429 Too Many Requests` → `RuntimeError`

## Testing

Run the tests with:

```bash
python -m unittest test_weather_client.py -v
```

All 11 tests should pass.

## Implementation Details

- Uses `requests.Session` for connection pooling
- Properly sets `X-API-Key` header for authentication
- Handles JSON serialization/deserialization automatically
- Includes comprehensive error handling
- Follows Python best practices with type hints and docstrings