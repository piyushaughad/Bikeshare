import urllib  # Import module for working with URLs
import json  # Import module for working with JSON data
import pandas as pd  # Import pandas for data manipulation
import folium  # Import folium for creating interactive maps
import datetime as dt  # Import datetime for working with dates and times
from geopy.distance import geodesic  # Import geodesic for calculating distances
from geopy.geocoders import Nominatim  # Import Nominatim for geocoding
import streamlit as st  # Import Streamlit for creating web apps
import time
import requests


@st.cache_data
def query_station_status_geojson(url):
    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())

    records = []

    for feature in data["features"]:
        props = feature["properties"].copy()
        lon, lat = feature["geometry"]["coordinates"]

        props["lon"] = lon
        props["lat"] = lat

        records.append(props)

    df = pd.DataFrame(records)

    # Filters (same as your original)
    df = df[df.is_renting == 1]
    df = df[df.is_returning == 1]

    df = df.drop_duplicates(["station_id", "last_reported"])

    # Convert timestamps
    df["last_reported"] = df["last_reported"].apply(
        lambda x: dt.datetime.utcfromtimestamp(x)
    )

    # Use last_reported as time index
    df = df.set_index("last_reported")
    df.index = df.index.tz_localize("UTC")

    # Expand bike types
    if "num_bikes_available_types" in df.columns:
        df = pd.concat([df, df["num_bikes_available_types"].apply(pd.Series)], axis=1)

    return df


@st.cache_data  # Cache the function's output to improve performance
def query_station_status(url):
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        data = json.loads(data_url.read().decode())  # Read and decode the JSON data

    df = pd.DataFrame(data["data"]["stations"])  # Convert the data to a DataFrame
    df = df[df.is_renting == 1]  # Filter out stations that are not renting
    df = df[df.is_returning == 1]  # Filter out stations that are not returning
    df = df.drop_duplicates(["station_id", "last_reported"])  # Remove duplicate records
    df.last_reported = df.last_reported.map(
        lambda x: dt.datetime.utcfromtimestamp(x)
    )  # Convert timestamps to datetime
    df["time"] = data["last_updated"]  # Add the last updated time to the DataFrame
    df.time = df.time.map(
        lambda x: dt.datetime.utcfromtimestamp(x)
    )  # Convert timestamps to datetime
    df = df.set_index("time")  # Set the time as the index
    df.index = df.index.tz_localize("UTC")  # Localize the index to UTC
    df = pd.concat(
        [df, df["num_bikes_available_types"].apply(pd.Series)], axis=1
    )  # Expand the bike types column

    return df  # Return the DataFrame


# Define the function to get station latitude and longitude from a given URL
def get_station_latlon(url):
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        latlon = json.loads(data_url.read().decode())  # Read and decode the JSON data
    latlon = pd.DataFrame(latlon["data"]["stations"])  # Convert the data to a DataFrame
    return latlon  # Return the DataFrame


# Function to determine marker color based on the number of bikes available
def get_marker_color(num_bikes_available):
    if num_bikes_available > 3:
        return "green"
    elif 0 < num_bikes_available <= 3:
        return "yellow"
    else:
        return "red"


# Define the function to geocode an address
def geocode(street="", city="", country="Ireland", retries=3, delay=1):
    # Combine all components into one query
    address_parts = [street, city, country]
    query = " ".join([part.strip() for part in address_parts if part.strip() != ""])

    geolocator = Nominatim(user_agent="bikeshare_streamlit_app")

    for attempt in range(retries):
        try:
            location = geolocator.geocode(query)
            if location is None:
                return ""  # Not found
            return (location.latitude, location.longitude)
        except Exception:
            time.sleep(delay)
            continue

    return ""  # Return empty if all retries fail


# Define the function to get bike availability near a location
def get_bike_availability(latlon, df):
    df = df.copy()

    # Only stations with at least one available bike
    df = df[df["num_bikes_available"] > 0]

    if df.empty:
        return []  # No bikes available

    # Calculate distance from user to each station
    df["distance"] = df.apply(
        lambda r: geodesic(latlon, (r["lat"], r["lon"])).km, axis=1
    )

    # Find the closest station
    closest_idx = df["distance"].idxmin()
    chosen_station = [
        df.loc[closest_idx, "station_id"],
        df.loc[closest_idx, "lat"],
        df.loc[closest_idx, "lon"],
    ]

    return chosen_station


# Define the function to get dock availability near a location
def get_dock_availability(latlon, df):
    df = df[df["num_docks_available"] > 0]

    if df.empty:
        return []  # No docks available

    # Vectorized distance calculation
    df["distance"] = df.apply(
        lambda r: geodesic(latlon, (r["lat"], r["lon"])).km, axis=1
    )

    # Find closest station
    closest_idx = df["distance"].idxmin()
    chosen_station = [
        df.loc[closest_idx, "station_id"],
        df.loc[closest_idx, "lat"],
        df.loc[closest_idx, "lon"],
    ]

    return chosen_station


# Define the function to run OSRM and get route coordinates and duration
def run_osrm(chosen_station, iamhere):
    start = "{},{}".format(iamhere[1], iamhere[0])  # Format the start coordinates
    end = "{},{}".format(
        chosen_station[2], chosen_station[1]
    )  # Format the end coordinates
    url = "http://router.project-osrm.org/route/v1/driving/{};{}?geometries=geojson".format(
        start, end
    )  # Create the OSRM API URL

    headers = {"Content-type": "application/json"}
    r = requests.get(url, headers=headers)  # Make the API request
    print("Calling API ...:", r.status_code)  # Print the status code

    routejson = r.json()  # Parse the JSON response
    coordinates = []
    i = 0
    lst = routejson["routes"][0]["geometry"]["coordinates"]
    while i < len(lst):
        coordinates.append([lst[i][1], lst[i][0]])  # Extract coordinates
        i = i + 1
    duration = round(
        routejson["routes"][0]["duration"] / 60, 1
    )  # Convert duration to minutes

    return coordinates, duration  # Return the coordinates and duration
