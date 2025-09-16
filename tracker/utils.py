import os

import googlemaps

MI_PER_M = 1 / 1609.344
KM_PER_M = 1 / 1000.0
API_KEY = os.environ.get("MAPS_API_KEY")

if not API_KEY:
    raise RuntimeError("API key not set")


class DistanceError(Exception):
    pass


def distance_miles(origin: str, destination: str, *, in_miles: bool = True) -> float:
    """Driving distance in miles between two addresses. 0.0 on failure."""
    gmaps = googlemaps.Client(key=API_KEY)
    res = gmaps.distance_matrix(origin, destination, mode="driving")  # type: ignore
    try:
        el = res["rows"][0]["elements"][0]
    except (KeyError, IndexError, TypeError) as e:
        raise DistanceError(f"Malformed response: {e}")

    if el.get("status") != "OK":
        raise DistanceError(f"Distance API failed: {el.get('status')}")
    meters = el["distance"]["value"]
    if in_miles:
        distance = meters * MI_PER_M
    else:
        distance = meters * KM_PER_M
    return round(distance, 1)
    # return 0.0


if __name__ == "__main__":
    print("Amsterdam → Alicante, Spain (both miles and km)")
    print(distance_miles("Amsterdam", "Alicante, Spain"))
    print(distance_miles("Amsterdam", "Alicante, Spain", in_miles=False))

    print("\nLouvre, Paris → Grand Place, Brussels (in km)")
    print(
        distance_miles(
            "Rue de Rivoli, 75001 Paris, France",
            "Grand Place, 1000 Brussels, Belgium",
            in_miles=False,
        )
    )

    print("\nTimes Square, New York → Central Park, New York (in miles)")
    print(
        distance_miles(
            "Times Square, New York, NY", "Central Park, New York, NY", in_miles=True
        )
    )
