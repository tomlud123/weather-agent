import sys
import requests


def fetch_weather(city: str, api_key: str):
    """
    Fetch current weather data for a given city using OpenWeatherMap API.

    Args:
        city (str): City name to fetch weather for.
        api_key (str): API key for OpenWeatherMap.

    Returns:
        tuple: (city_name, temperature_celsius, wind_speed_mps) if successful.

    Raises:
        SystemExit: On any error with a user-friendly message printed to stderr.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # temperature in Celsius
    }

    try:
        # Perform the HTTP GET request to the API endpoint
        response = requests.get(url, params=params, timeout=10)
        # Raise for status to catch HTTP 4xx/5xx errors
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: The request to the weather service timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Unable to connect to the weather service.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: HTTP error occurred - {http_err}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"Error: An error occurred while requesting weather data - {err}", file=sys.stderr)
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        print("Error: Failed to parse JSON response from the weather service.", file=sys.stderr)
        sys.exit(1)

    try:
        city_name = data["name"]
        temperature = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]
    except (KeyError, TypeError):
        print("Error: Unexpected data format received from the weather service.", file=sys.stderr)
        sys.exit(1)

    return city_name, temperature, wind_speed


if __name__ == "__main__":
    API_KEY = "your_api_key_here"  # Replace with your actual OpenWeatherMap API key
    DEFAULT_CITY = "Warszawa"

    weather = fetch_weather(DEFAULT_CITY, API_KEY)
    print(f"Weather in {weather[0]}:")
    print(f"Temperature: {weather[1]:.1f} °C")
    print(f"Wind Speed: {weather[2]:.1f} m/s")
