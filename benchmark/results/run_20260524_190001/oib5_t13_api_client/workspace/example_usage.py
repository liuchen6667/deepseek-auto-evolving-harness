#!/usr/bin/env python3
"""Example usage of WeatherClient"""

from weather_client import WeatherClient

def main():
    # Initialize client
    client = WeatherClient(api_key="your_api_key_here")
    
    print("=== Weather API Client Demo ===")
    
    try:
        # Example 1: Get current weather
        print("\n1. Getting current weather for Beijing:")
        current = client.get_current("Beijing")
        print(f"   City: {current['city']}")
        print(f"   Temperature: {current['temp_c']}°C")
        print(f"   Humidity: {current['humidity']}%")
        print(f"   Condition: {current['condition']}")
        
    except FileNotFoundError as e:
        print(f"   City not found: {e}")
    except Exception as e:
        print(f"   Error: {e}")
    
    try:
        # Example 2: Get forecast
        print("\n2. Getting 3-day forecast for Beijing:")
        forecast = client.get_forecast("Beijing", 3)
        print(f"   City: {forecast['city']}")
        print(f"   Days: {forecast['days']}")
        print(f"   Forecast data:")
        for day in forecast['forecast']:
            print(f"     {day['date']}: {day['condition']}, High: {day['high']}°C, Low: {day['low']}°C")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    try:
        # Example 3: Subscribe to alerts
        print("\n3. Subscribing to weather alerts:")
        alert = client.subscribe_alert(
            city="Beijing",
            threshold=35.0,
            callback_url="https://myapp.com/webhooks/weather"
        )
        print(f"   Alert ID: {alert['alert_id']}")
        print(f"   Status: {alert['status']}")
        
    except ValueError as e:
        print(f"   Bad request: {e}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 4: Error handling
    print("\n4. Testing error handling with invalid city:")
    try:
        invalid_result = client.get_current("InvalidCityName123")
    except FileNotFoundError as e:
        print(f"   Expected error caught: {e}")
    except Exception as e:
        print(f"   Other error: {e}")

if __name__ == "__main__":
    main()