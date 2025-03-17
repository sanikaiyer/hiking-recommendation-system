from sys import displayhook
from .utils import filter_trails
from django.shortcuts import render, get_object_or_404
from trails.models import Trail
from trails.utils import get_weather_by_location
from trails.utils import recommend_trails
import pandas as pd

# Load hiking trails data
hiking_trails_df = pd.read_csv('trails/hiking_trails.csv')

# Print column names to debug
print("Column Names in DataFrame:", hiking_trails_df.columns)

def trail_list(request):
    """
    Display a list of trails using data from the CSV file.
    """
    # Get filters from query parameters
    difficulty = request.GET.get('difficulty')
    location = request.GET.get('location')

    # Start with the entire DataFrame
    filtered_trails = hiking_trails_df

    # Apply filters if present
    if difficulty and difficulty != "Any":
        filtered_trails = filtered_trails[filtered_trails["Difficulty"] == difficulty]
    if location:
        filtered_trails = filtered_trails[filtered_trails["Location"].str.contains(location, case=False, na=False)]

    # Convert to a dictionary for rendering
    filtered_trails = filtered_trails.to_dict("records")

    return render(request, 'trails/trail_list.html', {'trails': filtered_trails})



def trail_detail(request, trail_id):
    """
    Display trail details along with weather information.
    """
    # Fetch the trail object
    trail = get_object_or_404(Trail, id=trail_id)

    # Get optional datetime from query parameters
    datetime = request.GET.get('datetime')  # Optional: Can be used for specific times

    # Fetch weather data for the trail's location
    location_coordinates = "37.8719,-122.2585"  # Static for now; dynamic in future
    temperature = get_weather_by_location(location_coordinates, datetime)

    # Handle unavailable weather data
    if temperature is not None:
        temperature_display = f"{temperature}°C"
    else:
        temperature_display = "Weather data is unavailable."

    # Prepare context for rendering
    context = {
        'trail': trail,
        'temperature': temperature_display,  # Ensure single °C
        'datetime': datetime or "Current Time",
    }
    return render(request, 'trails/trail_detail.html', context)

def recommendation_view(request):
    # Define dropdown options with "Any" included
    distance_ranges = [
        ("any", "Any"),  # Allow any distance
        ("0-5", "0-5 miles"),
        ("5-10", "5-10 miles"),
        ("10-15", "10-15 miles"),
        ("15+", "15+ miles"),
    ]
    elevation_ranges = [
        ("any", "Any"),  # Allow any elevation
        ("0-500", "0-500 ft"),
        ("500-1000", "500-1000 ft"),
        ("1000-2000", "1000-2000 ft"),
        ("2000+", "2000+ ft"),
    ]
    difficulty_levels = ["Any", "Easy", "Moderate", "Hard"]  # Include "Any" for difficulty

    # Default to empty results
    filtered_trails = []

    if request.method == "POST":
        selected_distance = request.POST.get("distance_range")
        selected_elevation = request.POST.get("elevation_range")
        selected_difficulty = request.POST.get("difficulty_level")

        # Parse range inputs for distance and elevation
        dist_min, dist_max = (selected_distance.split('-') + [None])[:2] if selected_distance != "any" else (None, None)
        elev_min, elev_max = (selected_elevation.split('-') + [None])[:2] if selected_elevation != "any" else (None, None)

        # Convert None to float('inf') or `0` for comparisons
        dist_max = float(dist_max) if dist_max else float('inf')
        elev_max = float(elev_max) if elev_max else float('inf')

        # Filter trails based on the selected criteria
        filtered_trails = hiking_trails_df[
            ((hiking_trails_df["Distance"] >= float(dist_min)) if dist_min else True) &
            ((hiking_trails_df["Distance"] <= float(dist_max)) if dist_max else True) &
            ((hiking_trails_df["Elevation"] >= float(elev_min)) if elev_min else True) &
            ((hiking_trails_df["Elevation"] <= float(elev_max)) if elev_max else True) &
            ((hiking_trails_df["Difficulty"] == selected_difficulty) if selected_difficulty != "Any" else True)
        ]

        # Sort trails by Rating in descending order
        filtered_trails = filtered_trails.sort_values(by="Rating", ascending=False)

        # Convert the filtered trails to a dictionary for display
        filtered_trails = filtered_trails.to_dict("records")

    context = {
        "distance_ranges": distance_ranges,
        "elevation_ranges": elevation_ranges,
        "difficulty_levels": difficulty_levels,
        "filtered_trails": filtered_trails,
    }
    return render(request, "trails/recommendation.html", context)