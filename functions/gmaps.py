from secret import keys
import requests
import streamlit as st
from src.gpt_function import gpt_function
import json
import math

def cal_distance(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = 6373 * c
    return d

@gpt_function
def search_nearby(keyword: str,
                  category: str,
                  radius: int = 1500,
                  minprice: int = 0,
                  maxprice: int = 4,
                  opennow: bool = False,
                  minrating: int = 0):
    """
    Useful for searching for places near to the user.
    Should only be used when the user explicitly asks for places near to them.
    :param keyword: a single keyword to associate with the places
    :param category: a single Google Maps category for the places to search for, e.g. "restaurant"
    :param radius: the radius in metres to search for places in
    :param minprice: the minimum price level of the places to search for (0-4)
    :param maxprice: the maximum price level of the places to search for (0-4)
    :param opennow: whether the places should be open right now
    :param minrating: the minimum rating of the places to search for (0-5)
    :return:
    """

    raw_location = st.session_state.raw_geo["coords"]
    latlong = f"{round(raw_location['latitude'], 6)},{round(raw_location['longitude'], 6)}"
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latlong}&radius={radius}&type={category}&keyword={keyword}&key={keys.gmaps_key}&opennow={opennow}&minprice={minprice}&maxprice={maxprice}"
    response = requests.get(url)
    results = json.loads(response.text)["results"]

    filtered = {"results": []}
    for result in results:
        if result["rating"] >= minrating:
            # Calculate the distance in km rounded to 2dp
            lat1 = raw_location["latitude"]
            lon1 = raw_location["longitude"]
            lat2 = result["geometry"]["location"]["lat"]
            lon2 = result["geometry"]["location"]["lng"]

            d = round(cal_distance(lat1, lon1, lat2, lon2), 2)

            filtered["results"].append({
                "place_id": result["place_id"],
                "name": result["name"],
                "address": result["vicinity"],
                "rating": result["rating"],
                "price_level": result["price_level"],
                "distance": str(d) + "km",
                "link": f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}",
            })

    filtered["results"] = filtered["results"][:10]

    return filtered

@gpt_function
def search_place(query: str,
                 location: str = "",
                 minprice: int = 0,
                 maxprice: int = 4,
                 opennow: bool = False,
                 minrating: int = 0):
    """
    Useful for searching for places. Can have a very broad query, e.g. "pizza in London".
    This will not provide any additional location information, so it is recommended to use the get_place_details function
    This will not provide coordiantes!
    :param query: the search query
    :param location: the latitude and longitude of the location to search in, e.g. "51.5074,0.1278"
    :param minprice: the minimum price level of the places to search for (0-4)
    :param maxprice: the maximum price level of the places to search for (0-4)
    :param opennow: whether the places should be open right now
    :param minrating: the minimum rating of the places to search for (0-5)
    """

    if location == "":
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={keys.gmaps_key}&opennow={opennow}&minprice={minprice}&maxprice={maxprice}"
    else:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={location}&key={keys.gmaps_key}&opennow={opennow}&minprice={minprice}&maxprice={maxprice}"

    response = requests.get(url)

    filtered = {"candidates": []}
    for result in json.loads(response.text)["results"]:
        if result["rating"] >= minrating:
            lat1 = st.session_state.raw_geo["coords"]["latitude"]
            lon1 = st.session_state.raw_geo["coords"]["longitude"]
            lat2 = result["geometry"]["location"]["lat"]
            lon2 = result["geometry"]["location"]["lng"]

            d = round(cal_distance(lat1, lon1, lat2, lon2), 2)

            rating = "N/A"
            if "rating" in result:
                rating = result["rating"]
            filtered["candidates"].append({
                "place_id": result["place_id"],
                "name": result["name"],
                "address": result["formatted_address"],
                "rating": rating,
                "distance": str(d) + "km",
                "link": f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}",
            })

    filtered = filtered["candidates"][:10]
    return filtered


@gpt_function
def get_place_details(place_id: str):
    """
    Useful for getting the details of a place. The address, phone number, website, opening hours, and link to Google Maps.

    :param place_id: the place ID of the place to get the details of
    """

    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={keys.gmaps_key}"
    response = requests.get(url)
    result = json.loads(response.text)["result"]

    formatted_result = {
        "name": result["name"],
        "address": result["formatted_address"],
        "rating": result["rating"],
        "link": f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}",
    }
    if "formatted_phone_number" in result:
        formatted_result["phone_number"] = result["formatted_phone_number"]
    if "website" in result:
        formatted_result["website"] = result["website"]
    if "opening_hours" in result:
        formatted_result["opening_hours"] = result["opening_hours"]["weekday_text"]

    return formatted_result


@gpt_function
def get_travel_distance(origin: str, destination: str, mode: str):
    """
    Useful for getting the travel distance and time between two locations.
    :param origin: The address of the origin location, e.g. "London, UK"
    :param destination: The address of the destination location, e.g. "Paris, France"
    :param mode: the mode of transport, can be one of: "walking", "driving", "transit", "bicycling"
    """


    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&mode={mode}&units=imperial&key={keys.gmaps_key}"
    response = requests.get(url)
    result = json.loads(response.text)["rows"][0]["elements"][0]

    if result["status"] != "OK":
        return result["status"]

    return {
        "distance": result["distance"]["text"],
        "duration": result["duration"]["text"],
    }

if __name__ == '__main__':
    print(get_travel_distance({
        "origin": "London, UK",
        "destination": "Paris, France",
        "mode": "driving",
        "reason": ""
    }))