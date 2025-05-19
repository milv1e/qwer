from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import requests
import os
import time
from functools import wraps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/maps'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Настройка OSRM
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"


class RouteCalculator:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="car_route_app", timeout=10)

    def get_coords(self, address):
        formats = [address, f"{address}, Россия", f"{address}, РФ"]
        for fmt in formats:
            try:
                location = self.geolocator.geocode(fmt)
                if location:
                    return (location.longitude, location.latitude)
            except Exception as e:
                print(f"Geocoding error: {e}")
        return None

    def get_road_route(self, start, end):
        try:
            url = f"{OSRM_URL}{start[0]},{start[1]};{end[0]},{end[1]}?overview=full&geometries=geojson"
            response = requests.get(url, timeout=15)
            data = response.json()

            if response.status_code == 200 and data.get('code') == 'Ok':
                route = data['routes'][0]
                return {
                    'distance': route['distance'] / 1000,
                    'duration': route['duration'] / 60,
                    'geometry': route['geometry']
                }
            return None
        except Exception as e:
            print(f"Routing error: {e}")
            return self.calculate_fallback_route(start, end)

    def calculate_fallback_route(self, start, end):
        distance = geodesic((start[1], start[0]), (end[1], end[0])).km
        avg_speed = 80 if distance > 100 else 30
        duration = (distance / avg_speed) * 1.2
        return {
            'distance': round(distance, 2),
            'duration': round(duration * 60, 2),
            'geometry': {
                'type': 'LineString',
                'coordinates': [start, end]
            }
        }


calculator = RouteCalculator()


# Маршруты
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/map', methods=['POST'])
def show_map():
    start = request.form['start'].strip()
    end = request.form['end'].strip()

    start_coords = calculator.get_coords(start)
    end_coords = calculator.get_coords(end)

    if not start_coords or not end_coords:
        error_msg = []
        if not start_coords:
            error_msg.append(f"Не удалось найти: '{start}'")
        if not end_coords:
            error_msg.append(f"Не удалось найти: '{end}'")
        return render_template('index.html',
                               error=". ".join(error_msg) + ". Уточните адреса.",
                               start=start,
                               end=end)

    route = calculator.get_road_route(start_coords, end_coords)
    if not route:
        return render_template('index.html',
                               error="Ошибка построения маршрута",
                               start=start,
                               end=end)

    m = folium.Map(
        location=[(start_coords[1] + end_coords[1]) / 2, (start_coords[0] + end_coords[0]) / 2],
        zoom_start=10 if route['distance'] > 100 else 12
    )

    folium.GeoJson(
        route['geometry'],
        style_function=lambda x: {'color': '#1e64c8', 'weight': 6}
    ).add_to(m)

    folium.Marker(
        [start_coords[1], start_coords[0]],
        popup=f"<b>Откуда:</b> {start}",
        icon=folium.Icon(color='green', icon='car')
    ).add_to(m)

    folium.Marker(
        [end_coords[1], end_coords[0]],
        popup=f"<b>Куда:</b> {end}",
        icon=folium.Icon(color='red', icon='flag')
    ).add_to(m)

    map_file = f"map_{int(time.time())}.html"
    m.save(os.path.join(app.config['UPLOAD_FOLDER'], map_file))

    return render_template('map.html',
                           start=start,
                           end=end,
                           distance=route['distance'],
                           duration=route['duration'],
                           map_file=map_file)


if __name__ == '__main__':
    app.run(debug=True)