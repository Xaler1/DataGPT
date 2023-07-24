import secret.keys as keys
from src.gpt_function import gpt_function
import json
import requests
import datetime
from geopy.geocoders import Nominatim
import streamlit as st

@gpt_function
def get_basic_info():
    """
    Useful for getting some basic information - the current time, the current date, the current location.
    """

    raw_location = st.session_state.raw_geo
    raw_location = raw_location["coords"]
    geolocator = Nominatim(user_agent="gpt-assistant")
    location = geolocator.reverse(f"{raw_location['latitude']}, {raw_location['longitude']}")
    address = location.raw["address"]
    return {"time": datetime.datetime.now().strftime("%H:%M"),
            "date": datetime.datetime.now().strftime("%d/%m/%Y"),
            "location": f"{address['city']}, {address['state']}, {address['country']}",
            "latlong": f"{raw_location['latitude']},{raw_location['longitude']}",
    }