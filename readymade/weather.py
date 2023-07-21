import secret.keys as keys
from src.gpt_function import gpt_function
import json
import requests

@gpt_function
def get_current_weather(location: str):
    """
    Useful for getting the weather at a location
    :param location: the location to get the weather for
    """
    url = f"https://api.weatherapi.com/v1/current.json?key={keys.weather_key}&q={location}&aqi=no"
    response = requests.get(url)
    json_data = json.loads(response.text)
    filtered = {
        "name": json_data["location"]["name"],
        "region": json_data["location"]["region"],
        "country": json_data["location"]["country"],
        "temp": json_data["current"]["temp_c"],
        "condition": json_data["current"]["condition"]["text"],
        "wind": json_data["current"]["wind_kph"],
        "wind_dir": json_data["current"]["wind_dir"],
        "humidity": json_data["current"]["humidity"],
        "cloud": json_data["current"]["cloud"],
        "feelslike": json_data["current"]["feelslike_c"],
    }
    return filtered
