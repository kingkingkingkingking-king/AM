"""
weather.py — Fetches current weather from OpenWeatherMap and returns
a natural spoken summary for Jarvis to read on startup.
"""

import requests
from am.core.config import WEATHER_API_KEY, WEATHER_CITY, WEATHER_UNITS


def get_weather_report() -> str:
    """
    Fetches current weather and returns a Jarvis-style spoken summary.
    Returns a fallback string if the request fails.
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY.strip() == "your_api_key_here":
        print("[Weather] API key not configured.")
        return ""

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q":     WEATHER_CITY.strip(),
            "appid": WEATHER_API_KEY.strip(),
            "units": WEATHER_UNITS.strip(),
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp        = round(data["main"]["temp"])
        feels_like  = round(data["main"]["feels_like"])
        description = data["weather"][0]["description"]
        humidity    = data["main"]["humidity"]
        city        = data["name"]
        unit_word   = "degrees Celsius" if WEATHER_UNITS == "metric" else "degrees Fahrenheit"

        report = (
            f"Current conditions in {city}: {description}, "
            f"{temp} {unit_word}, feels like {feels_like}. "
            f"Humidity is at {humidity} percent."
        )
        return report

    except requests.exceptions.ConnectionError:
        return "Unable to retrieve weather data, sir. No network connection."
    except requests.exceptions.Timeout:
        return "Weather request timed out, sir."
    except requests.exceptions.HTTPError as e:
        print(f"[Weather] HTTP error: {e} — check your API key in config.py")
        return ""
    except Exception as e:
        print(f"[Weather] Unexpected error: {e}")
        return ""


if __name__ == "__main__":
    report = get_weather_report()
    print(report if report else "[Weather] No report generated.")
