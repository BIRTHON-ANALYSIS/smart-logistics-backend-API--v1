from math import radians, sin, cos, sqrt, atan2

from .models import DriverLocation


EARTH_RADIUS_KM = 6371.0


def calculate_distance_km(driver,shipment):
    locations = list(
        DriverLocation.objects
        .filter(driver=driver, shipment=shipment)
        .order_by("recorded_at")
        .values("latitude", "longitude")
    )

    if len(locations) < 2:
        return 0.0

    total_distance = 0.0

    for previous, current in zip(
        locations,
        locations[1:],
    ):
        lat1 = radians(float(previous["latitude"]))
        lon1 = radians(float(previous["longitude"]))

        lat2 = radians(float(current["latitude"]))
        lon2 = radians(float(current["longitude"]))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        total_distance += EARTH_RADIUS_KM * c

    return round(total_distance, 2)