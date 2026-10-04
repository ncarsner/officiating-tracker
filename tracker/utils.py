import googlemaps
from django.conf import settings

MI_PER_M = 1 / 1609.344


class DistanceError(Exception):
    pass


def resolve_origin(user) -> str:
    """Origin address to measure driving distance from.

    The user's profile address wins when it is populated, otherwise
    ``settings.DEFAULT_ADDRESS``. Both the game form and the AJAX mileage
    preview resolve the origin through this function so the distance a user is
    shown cannot disagree with the distance that gets saved.

    Args:
        user: The user whose profile address to use. Accepts ``None`` and users
            with no related profile, both of which fall back to the default.

    Returns:
        The address to use as the origin. May be empty if neither a profile
        address nor a configured default is available.
    """
    profile = getattr(user, "profile", None)
    if profile is not None and profile.full_address:
        return profile.full_address
    return settings.DEFAULT_ADDRESS


def distance_miles(origin: str, destination: str) -> float:
    """Driving distance in miles between two addresses. 0.0 on failure."""
    try:
        gmaps = googlemaps.Client(key=settings.MAPS_API_KEY)
        res = gmaps.distance_matrix(origin, destination, mode="driving")  # type: ignore
    except Exception as e:
        raise DistanceError(f"API request failed: {e}")

    try:
        el = res["rows"][0]["elements"][0]
    except (KeyError, IndexError, TypeError) as e:
        raise DistanceError(f"Malformed response: {e}")

    if el.get("status") != "OK":
        raise DistanceError(f"Distance API failed: {el.get('status')}")
    meters = el["distance"]["value"]
    distance = meters * MI_PER_M
    return round(distance, 1)
