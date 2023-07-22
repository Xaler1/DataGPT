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

    forecast = []
    for hour in json_data["forecast"]["forecastday"][0]["hour"][::3]:
        forecast.append({
            "time": hour["time"].split(" ")[1],
            "temp_c": hour["temp_c"],
            "condition": hour["condition"]["text"],
            "wind_kph": hour["wind_kph"],
            "wind_dir": hour["wind_dir"],
            "chance_of_rain": hour["chance_of_rain"],
        })

    filtered = {
        "forecast": forecast
    }

    #If the user wants to know the weather for today, also include the current weather
    if day == datetime.datetime.now().strftime("%Y-%m-%d"):
        current = json_data["current"]
        filtered["current"] = {
            "temp_c": current["temp_c"],
            "condition": current["condition"]["text"],
            "wind_kph": current["wind_kph"],
            "wind_dir": current["wind_dir"],
            "precipitation_mm": current["precip_mm"],
        }
    return filtered
