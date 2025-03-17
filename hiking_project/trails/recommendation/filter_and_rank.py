from trails.models import Trail

def filter_and_rank(difficulty=None, max_distance=None, min_rating=None):
    # Filter trails
    trails = Trail.objects.all()
    if difficulty:
        trails = trails.filter(difficulty=difficulty)
    if max_distance:
        trails = trails.filter(distance__lte=max_distance)
    if min_rating:
        trails = trails.filter(rating__gte=min_rating)

    # Rank trails
    trails = sorted(trails, key=lambda t: (-t.rating, t.distance, t.elevation_gain))

    return trails
