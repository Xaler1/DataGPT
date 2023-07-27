import secret.keys as keys
from src.gpt_function import gpt_function
import json
import requests
import datetime

@gpt_function
def get_weather(location: str, day: str):
    """
    Useful for getting the weather at a location on a particular day
    :param location: the location to get the weather for
    :param day: the day to get the weather for. 'yyyy-mm-dd' format.
    """
    url = f"https://api.weatherapi.com/v1/forecast.json?key={keys.weather_key}&q={location}&dt={day}&aqi=no"
    response = requests.get(url)
    json_data = json.loads(response.text)

    forecast = {
        "time": [],
        "temp_c": [],
        "condition": [],
        "wind_kph": [],
        "wind_dir": [],
        "chance_of_rain": [],
    }
    for hour in json_data["forecast"]["forecastday"][0]["hour"][::2]:
        forecast["time"].append(hour["time"].split(" ")[1])
        forecast["temp_c"].append(hour["temp_c"])
        forecast["condition"].append(hour["condition"]["text"])
        forecast["wind_kph"].append(hour["wind_kph"])
        forecast["wind_dir"].append(hour["wind_dir"])
        forecast["chance_of_rain"].append(hour["chance_of_rain"])
    return forecast
