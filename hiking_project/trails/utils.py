from trails.models import Trail
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import joblib
import pandas as pd
import os
from hiking_project.settings import BASE_DIR

os.environ["PANDAS_ENABLE_BOTTLE_NECK"] = "0"


def filter_trails(difficulty=None, max_distance=None, min_rating=None):
    trails = Trail.objects.all()

    if difficulty:
        trails = trails.filter(difficulty=difficulty)
    if max_distance:
        trails = trails.filter(distance__lte=max_distance)
    if min_rating:
        trails = trails.filter(rating__gte=min_rating)

    return trails


def get_weather_by_location(location_coordinates="37.8719,-122.2585", datetime=None):
    """
    Fetch weather data using the Meteomatics API for a given location and datetime.
    """
    base_url = "https://api.meteomatics.com"
    datetime_str = datetime or "now"
    endpoint = f"/{datetime_str}/t_2m:C/{location_coordinates}/json"
    username = "personal_iyer_sanika"
    password = "W232nQKn8h"

    url = base_url + endpoint
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        # Extract temperature value from the response
        temperature = data['data'][0]['coordinates'][0]['dates'][0]['value']
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def recommend_trails(user_preferences):
    # Use the absolute path to the model
    model_path = os.path.join(BASE_DIR, 'trails', 'models', 'trail_recommendation_model.pkl')

    # Debugging: print model path
    print(f"Loading model from: {model_path}")

    # Load the model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    model = joblib.load(model_path)
    print("Model loaded successfully.")

    # Your recommendation logic here...

