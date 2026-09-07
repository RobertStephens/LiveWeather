import argparse
import os
from pprint import pprint
import httpx2
from dotenv import load_dotenv


# Define the URL for the APIs with placeholders
OPENWEATHERMAP_URL_BASE = "https://api.openweathermap.org/data/2.5/weather"
#OPENWEATHERMAP_URL_BASE = "https://api.openweathermap.org/data/4.0/onecall/current"
WEATHERSTACK_URL_BASE = "http://api.weatherstack.com/current"


def kelvin_to_celcius(temp) -> float:
    zero_celcius_in_kelvin = 273.15
    return round(temp - zero_celcius_in_kelvin, 2)

def sanitize_inputs(lat: float, lon: float) -> tuple:
    if lat > 90.0:
        lat = 90.0
    elif lat < -90.0:
        lat = -90.0

    if lon > 180.0:
        lon = 180.0
    elif lon < -180.0:
        lon = -180.0

    return lat, lon

def current_weather(args: argparse.ArgumentParser) -> list[dict]:

    weather_data = []

    if args.city:
        params_openweathermap = {"q": args.city}
    else:
        params_openweathermap = {"lat": args.lat, "lon": args.lon}

    load_dotenv()  # Loads .env into os.environ

    appid = os.getenv("OPENWEATHERMAP_API_KEY")

    if not appid:
        print("Warning: OPENWEATHERMAP_API_KEY is not set, aborting")
        return

    params_openweathermap["appid"] = appid

    response_openweathermap = httpx2.get(
        OPENWEATHERMAP_URL_BASE, params=params_openweathermap, timeout=10
    )
    
    weather_json = response_openweathermap.json()

    weather_json['main']['celcius_temp_min'] = kelvin_to_celcius(weather_json['main']['temp_min'])
    weather_json['main']['celcius_temp_max'] = kelvin_to_celcius(weather_json['main']['temp_max'])
    weather_json['main']['celcius_temp'] = kelvin_to_celcius(weather_json['main']['temp'])
    weather_json['main']['celcius_feels_like'] = kelvin_to_celcius(weather_json['main']['feels_like'])
    
    weather_data.append({"OpenWeatherMap": weather_json})

    if not weather_data:
        raise ValueError("No API keys provided or no valid data returned.")
    return weather_data


if __name__ == "__main__":
    default_lat = 51.5074
    default_lon = -0.1278
    default_city = ""

    parser = argparse.ArgumentParser(description="Get current weather data for a given location.")

    parser.add_argument(
        "-t", "--lat", type=float, nargs="?", default=default_lat, help="Latitude of the location"
    )
    parser.add_argument(
        "-n", "--lon", type=float, nargs="?", default=default_lon, help="Longitude of the location"  
    )
    parser.add_argument(
        "-c", "--city", type=str, nargs="?", default=default_city, help="City name (optional)"
    )
    parser.add_argument(
        '-v', '--version', 
            action='version',
            version='%(prog)s 0.1', 
            help="Use either latitude and longitude or city name"
    )

    args = parser.parse_args()

    args.lat, args.lon = sanitize_inputs(args.lat, args.lon)

    try:
        weather_data = current_weather(args)
        for forecast in weather_data:
            pprint(forecast)
    except ValueError as e:
        print(repr(e))
        location = ""
