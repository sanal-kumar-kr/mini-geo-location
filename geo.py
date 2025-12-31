from redis_client import redis_client
REDIS_MIN_LAT = -85.05112878
REDIS_MAX_LAT = 85.05112878
REDIS_MIN_LON = -180
REDIS_MAX_LON = 180
def clamp_coordinates_for_redis(latitude: float, longitude: float):
    latitude = max(min(latitude, REDIS_MAX_LAT), REDIS_MIN_LAT)
    longitude = max(min(longitude, REDIS_MAX_LON), REDIS_MIN_LON)
    return latitude, longitude
def safe_geoadd(key: str, longitude: float, latitude: float, member: str):
    try:
        return redis_client.geoadd(key, longitude, latitude, member)
    except Exception:
        return redis_client.execute_command(
            "GEOADD", key, longitude, latitude, member
        )
