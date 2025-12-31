# Driver Geo Service API Documentation

## Base URL

```
http://127.0.0.1/:8000
```

---

## 1. Create Driver

**Endpoint:** `POST /drivers`

**Request Body:**

```json
{
  "name": "Sanal Kumar",
  "phone": "+919876543210"
}
```

**Response:**

```json
{
  "message": "Driver created",
  "driver_id": 1
}
```

---

## 2. Update Driver Location

**Endpoint:** `POST /drivers/{driver_id}/location`

**Path Parameters:**

* `driver_id` (int) - ID of the driver

**Request Body:**

```json
{
  "latitude": -90,
  "longitude": -180
}
```

**Response:**

```json
{
  "message": "Driver location updated",
  "redis_result": 1,
  "coordinates": {
    "original": {"lat": -90, "lon": -180},
    "clamped": {"lat": -85.05112878, "lon": -180}
  }
}
```

---

## 3. Find Nearby Drivers

**Endpoint:** `GET /drivers/nearby`

**Query Parameters:**

* `lat` (float) - Latitude of search center (-90 to 90)
* `lng` (float) - Longitude of search center (-180 to 180)
* `radius_km` (float) - Radius in kilometers (greater than 0)

**Example Request:**

```
GET /drivers/nearby?lat=0&lng=0&radius_km=10000
```

**Response:**

```json
{
  "nearby_drivers": [
    {"driver_id": 2, "distance_km": 0.0},
    {"driver_id": 3, "distance_km": 6890.23},
    {"driver_id": 4, "distance_km": 5570.12}
  ]
}
```

---

## 4. Route Information

**Endpoint:** `GET /route-info`

**Query Parameters:**

* `from_lat` (float) - Start latitude (-90 to 90)
* `from_lng` (float) - Start longitude (-180 to 180)
* `to_lat` (float) - End latitude (-90 to 90)
* `to_lng` (float) - End longitude (-180 to 180)

**Example Request:**

```
GET /route-info?from_lat=-89.9&from_lng=-179.9&to_lat=-89.8&to_lng=-179.8
```

**Response:**

```json
{
  "distance_km": 15.43,
  "duration_minutes": 18
}
```

---

## Notes

* Latitude and longitude are automatically clamped for Redis operations.
* MySQL stores the original latitude and longitude values.
* Redis stores clamped coordinates to prevent GEOADD errors.
* Redis GEO search supports sorting by nearest distance.
* Mapbox API is used for route distance and duration calculations.
* All endpoints return proper HTTP status codes for errors.
