"""
VOID — Weather Service
OpenWeatherMap API for Vizag weather in daily brief
"""

from typing import Optional
import requests
from config import OPENWEATHER_API_KEY, DEFAULT_CITY


def get_weather(city: str = DEFAULT_CITY) -> Optional[str]:
    """Get weather for a city. Returns formatted string or None on failure."""
    if not OPENWEATHER_API_KEY:
        return "Weather API key set cheyyaledhu bro — .env lo OPENWEATHER_API_KEY add cheyyi."

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "en",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        temp = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        condition = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = round(data["wind"]["speed"], 1)
        city_name = data["name"]

        emoji_map = {
            "clear": "☀️",
            "cloud": "☁️",
            "rain": "🌧️",
            "drizzle": "🌦️",
            "thunder": "⛈️",
            "snow": "❄️",
            "mist": "🌫️",
            "fog": "🌫️",
            "haze": "🌫️",
        }
        emoji = "🌤️"
        for key, e in emoji_map.items():
            if key in condition.lower():
                emoji = e
                break

        return (
            f"{emoji} {city_name} lo {temp}°C ({feels_like}°C feels like), "
            f"{condition}. Humidity: {humidity}%, Wind: {wind} m/s."
        )
    except requests.ConnectionError:
        return None  # Network issue — caller handles fallback
    except requests.HTTPError as e:
        if resp.status_code == 401:
            return "Weather API key invalid bro — check OPENWEATHER_API_KEY in .env"
        return None
    except Exception:
        return None


def get_weather_short(city: str = DEFAULT_CITY) -> str:
    """Short one-liner for daily brief — never fails."""
    result = get_weather(city)
    if result:
        return result
    return f"🌤️ Vizag — weather fetch avvaledhu (API key or network issue)"
