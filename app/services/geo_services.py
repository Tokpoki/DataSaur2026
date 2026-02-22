from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # радиус Земли в км

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

from sqlalchemy.orm import Session
from ..models import BusinessUnit


def find_nearest_office(db: Session, client_lat, client_lon):

    offices = db.query(BusinessUnit).all()

    nearest_office = None
    min_distance = float("inf")

    for office in offices:
        if office.latitude and office.longitude:

            distance = haversine(
                float(client_lat),
                float(client_lon),
                float(office.latitude),
                float(office.longitude),
            )

            if distance < min_distance:
                min_distance = distance
                nearest_office = office

    return nearest_office