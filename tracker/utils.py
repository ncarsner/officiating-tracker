import googlemaps
from django.conf import settings

MI_PER_M = 1 / 1609.344


class DistanceError(Exception):
    pass


def distance_miles(origin: str, destination: str) -> float:
    """Driving distance in miles between two addresses. 0.0 on failure."""
    gmaps = googlemaps.Client(key=settings.MAPS_API_KEY)
    res = gmaps.distance_matrix(origin, destination, mode="driving")  # type: ignore
    try:
        el = res["rows"][0]["elements"][0]
    except (KeyError, IndexError, TypeError) as e:
        raise DistanceError(f"Malformed response: {e}")

    if el.get("status") != "OK":
        raise DistanceError(f"Distance API failed: {el.get('status')}")
    meters = el["distance"]["value"]
    distance = meters * MI_PER_M
    return round(distance, 1)
