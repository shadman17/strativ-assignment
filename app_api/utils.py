from app_core.models import District


def get_nearest_district(latitude: float, longitude: float):
    """Return nearest district using simple squared Euclidean distance."""
    districts = District.objects.all()
    nearest_district = None
    nearest_distance = None

    for district in districts:
        lat_diff = float(district.latitude) - latitude
        lon_diff = float(district.longitude) - longitude
        distance = (lat_diff * lat_diff) + (lon_diff * lon_diff)

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_district = district

    return nearest_district
