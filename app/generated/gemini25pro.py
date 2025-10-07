"""
A standalone script to fetch current weather data from the OpenWeatherMap API.

This script demonstrates best practices for making API calls in Python, including
robust error handling and secure management of API keys.
"""

import os
import sys
import requests

# --- Configuration ---
# It is best practice to store sensitive data like API keys in environment
# variables rather than hardcoding them in the script.
# To run this script, set the OWM_API_KEY environment variable:
# export OWM_API_KEY='your_actual_api_key'
API_KEY = os.getenv("OWM_API_KEY")
DEFAULT_CITY = "Warszawa"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> tuple[str, float, float] | None:
    """
    Fetches, parses, and returns weather data for a specified city.

    Args:
        city: The name of the city for which to retrieve weather data.

    Returns:
        A tuple containing the city name, temperature in Celsius, and wind
        speed in m/s if the request is successful. Returns None on failure.
    """
    if not API_KEY:
        print(
            "Error: OpenWeatherMap API key is not set.",
            file=sys.stderr
        )
        print(
            "Please set the OWM_API_KEY environment variable.",
            file=sys.stderr
        )
        sys.exit(1)

    # Parameters for the API request
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Request temperature in Celsius
    }

    try:
        # Perform the HTTP GET request with a timeout
        response = requests.get(BASE_URL, params=params, timeout=10)

        # Check for HTTP errors (e.g., 404 Not Found, 401 Unauthorized)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract relevant weather information
        city_name = data.get("name", "N/A")
        temperature = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]

        return city_name, temperature, wind_speed

    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., DNS failure, connection refused)
        print(f"Error: A network problem occurred: {e}", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP error codes from the server
        print(f"Error: HTTP Error: {e}", file=sys.stderr)
        return None
    except requests.exceptions.JSONDecodeError:
        # Handle cases where the response is not valid JSON
        print("Error: Failed to parse server response as JSON.", file=sys.stderr)
        return None
    except KeyError as e:
        # Handle missing keys in the JSON response
        print(f"Error: Unexpected data format from API. Missing key: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    # Use the default city if no command-line argument is provided
    city_to_check = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CITY

    print(f"Fetching weather data for {city_to_check}...")
    weather_data = get_weather(city_to_check)

    # If data was fetched successfully, print it in a user-friendly format
    if weather_data:
        name, temp, wind = weather_data
        print("\n--- Current Weather ---")
        print(f"Location: {name}")
        print(f"Temperature: {temp:.1f}°C")
        print(f"Wind Speed: {wind} m/s")
        print("-----------------------")
    else:
        # A more specific error message will have already been printed
        print("Failed to retrieve weather data.", file=sys.stderr)
        sys.exit(1)