from helpers import *
import streamlit as st
import folium
from streamlit_folium import folium_static
import time
import json

station_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status.json"
location_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information"

One_url = "https://data.smartdublin.ie/dublinbikes-api/bikes/dublin_bikes/current/stations.geojson"

st.title("Toronto Bike share station status")
st.markdown(
    "This Dashboard track bike availability at each bike share station in Toronto."
)


# data_df = query_station_status(station_url)  # Get station status data
# latlon_df = get_station_latlon(location_url)  # Get station latitude and longitude data
# data = join_latlon(data_df, latlon_df)  # Join the status data with the location data

data = query_station_status_geojson(One_url)

col1, col2, col3 = st.columns(3)  # Create three columns for metrics
with col1:
    st.metric(
        label="Bikes Available Now", value=sum(data["num_bikes_available"])
    )  # Display total number of bikes available
    st.metric(
        label="Capacity of station", value=sum(data["capacity"])
    )  # Display total number of e-bikes available
with col2:
    st.metric(
        label="Stations with Available Bikes",
        value=len(data[data["num_bikes_available"] > 0]),
    )  # Display number of stations with available bikes
    st.metric(
        label="Stations have a Available Capacity",
        value=len(data[data["capacity"] > 0]),
    )  # Display number of stations with available e-bikes
with col3:
    st.metric(
        label="Stations with Empty Docks",
        value=len(data[data["num_docks_available"] > 0]),
    )  # Display number of stations with empty docks


iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False
input_bike_modes = []

with st.sidebar:
    bike_method = st.selectbox(
        "Are you looking to rent or return a bike?", ("Rent", "Return")
    )  # Selection box for rent or return
    if bike_method == "Rent":
        st.subheader("Where are you located?")
        input_street = st.text_input("street", "")
        input_city = st.text_input("City", "Dublin")
        input_country = st.text_input("Country", "Ireland")
        input_eircode = st.text_input("Eircode (optional)")
        drive = st.checkbox("I'm driving there")
        findmeabike = st.button("Find me a bike!", type="primary")
        if findmeabike:
            if input_street != "":
                iamhere = geocode(
                    input_street, input_city, input_country, input_eircode
                )
                if iamhere == "":
                    st.subheader(":red[Input address not valid!]")
            else:
                st.subheader(":red[Input address not valid!]")
    elif bike_method == "Return":
        st.subheader("Where are you located?")
        input_street_return = st.text_input("street", "")
        input_city_return = st.text_input("City", "Dublin")
        input_country_return = st.text_input("Country", "Ireland")
        input_eircode_return = st.text_input("Eircode (optional)")
        findmeadock = st.button("Find me a dock!", type="primary")
        if findmeadock:
            if input_street_return != "":
                iamhere_return = geocode(
                    input_street_return,
                    input_city_return,
                    input_country_return,
                    input_eircode_return,
                )
                if iamhere_return == "":
                    st.subheader(":red[Input address not valid!]")
            else:
                st.subheader(":red[Input address not valid!]")

if bike_method == "Return" and findmeadock == False:
    center = [53.3440956, -6.2674862]  # Coordinates for Toronto
    m = folium.Map(
        location=center, zoom_start=13, tiles="cartodbpositron"
    )  # Create a map with a grey background
    for _, row in data.iterrows():
        marker_color = get_marker_color(
            row["num_bikes_available"]
        )  # Determine marker color based on bikes available
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"Station ID: {row['station_id']}<br>"
                f"Total Bikes Available: {row['num_bikes_available']}<br>"
                f"Total Docks Available: {row['num_docks_available']}<br>"
                f"Capacity Available: {row['capacity']}",
                max_width=300,
            ),
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app


if bike_method == "Rent" and findmeabike == False:
    center = [53.3440956, -6.2674862]  # Coordinates for Toronto
    m = folium.Map(
        location=center, zoom_start=13, tiles="cartodbpositron"
    )  # Create a map with a grey background
    for _, row in data.iterrows():
        marker_color = get_marker_color(
            row["num_bikes_available"]
        )  # Determine marker color based on bikes available
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"Station ID: {row['station_id']}<br>"
                f"Total Bikes Available: {row['num_bikes_available']}<br>"
                f"Total Docks Available: {row['num_docks_available']}<br>"
                f"Capacity Available: {row['capacity']}",
                max_width=300,
            ),
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app


if findmeabike:
    if input_street != "":
        if iamhere != "":
            chosen_station = get_bike_availability(
                iamhere, data
            )  # Get bike availability (id, lat, lon)
            center = iamhere  # Center the map on user's location
            m1 = folium.Map(
                location=center, zoom_start=16, tiles="cartodbpositron"
            )  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(
                    row["num_bikes_available"]
                )  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"Station ID: {row['station_id']}<br>"
                        f"Total Bikes Available: {row['num_bikes_available']}<br>"
                        f"Total Docks Available: {row['num_docks_available']}<br>"
                        f"Capacity Available: {row['capacity']}",
                        max_width=300,
                    ),
                ).add_to(m1)
            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa"),
            ).add_to(m1)
            folium.Marker(
                location=(chosen_station[1], chosen_station[2]),
                popup="Rent your bike here.",
                icon=folium.Icon(color="red", icon="bicycle", prefix="fa"),
            ).add_to(m1)
            coordinates, duration = run_osrm(
                chosen_station, iamhere
            )  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(
                    label=":green[Travel Time (min)]", value=duration
                )  # Display travel time

# if findmeadock:
if findmeadock:
    if input_street_return != "":
        if iamhere_return != "":
            chosen_station = get_dock_availability(
                iamhere_return, data
            )  # Get dock availability (id, lat, lon)
            center = iamhere_return  # Center the map on user's location
            m1 = folium.Map(
                location=center, zoom_start=16, tiles="cartodbpositron"
            )  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(
                    row["num_bikes_available"]
                )  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"Station ID: {row['station_id']}<br>"
                        f"Total Bikes Available: {row['num_bikes_available']}<br>"
                        f"Total Docks Available: {row['num_docks_available']}<br>"
                        f"Capacity Available: {row['capacity']}",
                        max_width=300,
                    ),
                ).add_to(m1)
            folium.Marker(
                location=iamhere_return,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa"),
            ).add_to(m1)
            folium.Marker(
                location=(chosen_station[1], chosen_station[2]),
                popup="Return your bike here.",
                icon=folium.Icon(color="red", icon="bicycle", prefix="fa"),
            ).add_to(m1)
            coordinates, duration = run_osrm(
                chosen_station, iamhere_return
            )  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(
                    label=":green[Travel Time (min)]", value=duration
                )  # Display travel time
