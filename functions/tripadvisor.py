import json

from secret import keys
import requests
from src.gpt_function import gpt_function
import streamlit as st

@gpt_function
def search_places(query: str, category: str = ""):
    """
    Useful for searching for places.

    :param query: the search query.
    :param category: the category of place. Can be only one of: restaurants, hotels, attractions
    """

    if category == "":
        response = requests.get(f"https://api.content.tripadvisor.com/api/v1/location/search?key={keys.tripadvisor_key}&searchQuery={query}")
    else:
        response = requests.get(f"https://api.content.tripadvisor.com/api/v1/location/search?key={keys.tripadvisor_key}&searchQuery={query}&category={category}")

    results = json.loads(response.text)["data"]

    filtered = {"results": []}
    for result in results:
        filtered["results"].append({
            "location_id": result["location_id"],
            "name": result["name"],
            "address": result["address_obj"]["address_string"]
        })


    return filtered


@gpt_function
def find_nearby(category:str):
    """
    Useful for finding places near to the user  .

    :param category: the category of place. Can be only one of: restaurants, hotels, attractions
    """

    raw_location = st.session_state.raw_geo["coords"]
    # Get rounded lat and long
    latlong = f"{round(raw_location['latitude'], 6)},{round(raw_location['longitude'], 6)}"

    response = requests.get(f"https://api.content.tripadvisor.com/api/v1/location/nearby_search?latLong={latlong}&key={keys.tripadvisor_key}&category={category}")

    results = json.loads(response.text)["data"]

    filtered = {"results": []}
    for result in results:
        filtered["results"].append({
            "location_id": result["location_id"],
            "name": result["name"],
            "distance": str(round(float(result["distance"]), 2)) + "mi",
            "address": result["address_obj"]["address_string"]
        })

    return filtered