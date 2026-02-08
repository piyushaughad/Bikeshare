# 🚲 Bike Share Station Dashboard

An interactive **Streamlit web application** that visualizes real-time bike share station data and helps users find the nearest available bike or dock based on their location.

The app displays live station availability, interactive maps, and route directions using OpenStreetMap and OSRM.

---

## ✨ Features

- 📊 Live station metrics
  - Total bikes available
  - Station capacity
  - Stations with available bikes
  - Stations with empty docks
- 🗺️ Interactive map with color-coded stations
- 📍 Find nearest bike or dock based on user location
- 🧭 Route visualization and estimated travel time
- ⚡ Cached API calls for improved performance

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Folium
- GeoPy
- OSRM API
- OpenStreetMap / GeoJSON bike share data

---

## 📁 Project Structure

.
├── app.py # Main Streamlit application

├── helpers.py # Helper functions (API, geocoding, routing)

├── environment.yml # Conda environment configuration

└── README.md # Project documentation


---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/bike-share-dashboard.git
cd bike-share-dashboard

2. Create and activate the Conda environment

```bash
conda env create -f environment.yml
conda activate bike-share

3. Run the application

streamlit run app.py

The app will open automatically in your browser.

🧑‍💻 How It Works

1. Fetches real-time bike station data from a public GeoJSON API

2. Filters active stations (renting and returning enabled)

3. Displays stations on an interactive Folium map

4. Geocodes user-entered addresses

5. Finds the closest station with bikes or docks

6. Calculates route and travel time using OSRM

| Color     | Meaning                     |
| --------- | --------------------------- |
| 🟢 Green  | More than 3 bikes available |
| 🟡 Yellow | 1–3 bikes available         |
| 🔴 Red    | No bikes available          |


🌍 Data Sources

Public Bike Share GeoJSON APIs
OpenStreetMap
OSRM (Open Source Routing Machine)

⚠️ Limitations

Geocoding is rate-limited (OpenStreetMap Nominatim)
Requires internet access for live data
Routing uses driving mode by default


📌 Future Improvements

Walking and cycling route options
Multi-city support
Favorite stations
Availability alerts
Mobile-friendly UI
