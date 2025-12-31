from fastapi import FastAPI, HTTPException, Query
import requests
import os
from dotenv import load_dotenv
from db import get_db
from redis_client import redis_client, GEO_KEY
from models import DriverCreate, DriverLocationUpdate
from utils.geo import clamp_coordinates_for_redis, safe_geoadd
load_dotenv()
app = FastAPI(title="Driver Geo Service")
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
@app.post("/drivers")
def create_driver(data: DriverCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO drivers (name, phone) VALUES (%s, %s)",
        (data.name, data.phone)
    )
    db.commit()
    driver_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "Driver created", "driver_id": driver_id}
@app.post("/drivers/{driver_id}/location")
def update_driver_location(driver_id: int, data: DriverLocationUpdate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM drivers WHERE id=%s", (driver_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Driver not found")
    cursor.execute("""
        INSERT INTO driver_locations (driver_id, latitude, longitude)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        latitude=VALUES(latitude),
        longitude=VALUES(longitude)
    """, (driver_id, data.latitude, data.longitude))
    db.commit()
    lat, lng = clamp_coordinates_for_redis(data.latitude, data.longitude)
    safe_geoadd(GEO_KEY, lng, lat, f"driver:{driver_id}")
    cursor.close()
    db.close()
    return {"message": "Location updated"}
@app.get("/drivers/nearby")
def find_nearby_drivers(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0)
):
    lat, lng = clamp_coordinates_for_redis(lat, lng)
    results = redis_client.georadius(
        GEO_KEY,
        lng,
        lat,
        radius_km,
        unit="km",
        withdist=True,
        sort="ASC"
    )
    drivers = [
        {
            "driver_id": int(member.replace("driver:", "")),
            "distance_km": round(float(dist), 2)
        }
        for member, dist in results
    ]
    return {"nearby_drivers": drivers}
@app.get("/route-info")
def route_info(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float
):
    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/driving/"
        f"{from_lng},{from_lat};{to_lng},{to_lat}"
        f"?access_token={MAPBOX_TOKEN}"
    )
    res = requests.get(url, timeout=10)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Mapbox error")
    route = res.json()["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_minutes": round(route["duration"] / 60)
    }
