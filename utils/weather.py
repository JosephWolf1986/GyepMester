"""utils/weather.py – OpenWeatherMap API hívások."""
import requests


def get_weather(city, api_key):
    """
    Lekéri az aktuális időjárást a megadott városra.
    Visszaad egy dict-et vagy None-t hiba esetén.
    """
    if not api_key or not city:
        return None

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',
            'lang': 'hu',
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return None

        data = resp.json()
        return {
            'city': data['name'],
            'temp': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon'],
            'icon_url': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s → km/h
            'rain_1h': data.get('rain', {}).get('1h', 0),
            'rain_3h': data.get('rain', {}).get('3h', 0),
        }
    except Exception:
        return None


def get_forecast(city, api_key, days=3):
    """
    Lekéri az előrejelzést (5 nap, 3 órás lépésben) és összegezi naponként.
    """
    if not api_key or not city:
        return []

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',
            'lang': 'hu',
            'cnt': days * 8,  # 8 * 3h = 24h / nap
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return []

        data = resp.json()
        from datetime import datetime
        daily = {}

        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            day_key = dt.date()
            if day_key not in daily:
                daily[day_key] = {
                    'date': day_key,
                    'temp_max': item['main']['temp_max'],
                    'temp_min': item['main']['temp_min'],
                    'rain': item.get('rain', {}).get('3h', 0),
                    'description': item['weather'][0]['description'].capitalize(),
                    'icon': item['weather'][0]['icon'],
                }
            else:
                daily[day_key]['temp_max'] = max(daily[day_key]['temp_max'],
                                                  item['main']['temp_max'])
                daily[day_key]['temp_min'] = min(daily[day_key]['temp_min'],
                                                  item['main']['temp_min'])
                daily[day_key]['rain'] += item.get('rain', {}).get('3h', 0)

        return list(daily.values())[:days]
    except Exception:
        return []
