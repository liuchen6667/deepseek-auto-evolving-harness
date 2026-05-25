#!/usr/bin/env python3
"""Example usage of the WeatherClient."""

from weather_client import WeatherClient

# Example 1: Basic usage
print("=== Example 1: Basic Usage ===")
client = WeatherClient(api_key="your_api_key_here")

try:
    # Get current weather
    print("Getting current weather for Beijing...")
    current = client.get_current("Beijing")
    print(f"Current weather: {current['temp_c']}°C, {current['condition']}")
    
    # Get forecast
    print("\nGetting 3-day forecast for Beijing...")
    forecast = client.get_forecast("Beijing", days=3)
    print(f"Forecast for {forecast['city']} ({forecast['days']} days):")
    for day in forecast["forecast"]:
        print(f"  {day['date']}: {day['high']}/{day['low']}°C, {day['condition']}")
    
    # Subscribe to alerts
    print("\nSubscribing to alerts for Beijing...")
    alert = client.subscribe_alert(
        city="Beijing",
        threshold=35.0,
        callback_url="https://example.com/webhook"
    )
    print(f"Alert created: ID={alert['alert_id']}, Status={alert['status']}")
    
except ValueError as e:
    print(f"Bad request error: {e}")
except PermissionError as e:
    print(f"Authentication error: {e}")
except FileNotFoundError as e:
    print(f"City not found: {e}")
except RuntimeError as e:
    print(f"Rate limit error: {e}")
except Exception as e:
    print(f"Other error: {e}")

client.close()

# Example 2: Using context manager
print("\n\n=== Example 2: Using Context Manager ===")
with WeatherClient(api_key="your_api_key_here") as client:
    try:
        current = client.get_current("Shanghai")
        print(f"Shanghai: {current['temp_c']}°C, {current['condition']}")
    except Exception as e:
        print(f"Error: {e}")

# Example 3: Error handling demonstration
print("\n\n=== Example 3: Error Handling ===")
client = WeatherClient(api_key="invalid_key")

# These would raise exceptions in real usage:
# try:
#     client.get_current("UnknownCity")  # Would raise FileNotFoundError (404)
# except FileNotFoundError as e:
#     print(f"Expected error: {e}")
# 
# try:
#     client.get_current("")  # Would raise ValueError (400)
# except ValueError as e:
#     print(f"Expected error: {e}")

print("\nNote: To see actual API calls, replace 'your_api_key_here' with a real API key")
print("and uncomment the error handling examples.")