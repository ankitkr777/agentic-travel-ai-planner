from langchain.tools import tool
import math

# Approximate lat/lon for common cities — used to estimate flight distance & cost
CITY_COORDS = {
    "nyc": (40.7128, -74.0060), "new york": (40.7128, -74.0060),
    "london": (51.5074, -0.1278), "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503), "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198), "sydney": (-33.8688, 151.2093),
    "los angeles": (34.0522, -118.2437), "la": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298), "toronto": (43.6532, -79.3832),
    "frankfurt": (50.1109, 8.6821), "amsterdam": (52.3676, 4.9041),
    "bangkok": (13.7563, 100.5018), "istanbul": (41.0082, 28.9784),
    "rome": (41.9028, 12.4964), "barcelona": (41.3851, 2.1734),
    "berlin": (52.5200, 13.4050), "madrid": (40.4168, -3.7038),
    "mumbai": (19.0760, 72.8777), "delhi": (28.6139, 77.2090),
    "beijing": (39.9042, 116.4074), "shanghai": (31.2304, 121.4737),
    "hong kong": (22.3193, 114.1694), "seoul": (37.5665, 126.9780),
    "cairo": (30.0444, 31.2357), "nairobi": (-1.2921, 36.8219),
    "mexico city": (19.4326, -99.1332), "sao paulo": (-23.5505, -46.6333),
    "buenos aires": (-34.6037, -58.3816), "johannesburg": (-26.2041, 28.0473),
    "athens": (37.9838, 23.7275), "lisbon": (38.7223, -9.1393),
    "vienna": (48.2082, 16.3738), "prague": (50.0755, 14.4378),
    "miami": (25.7617, -80.1918), "san francisco": (37.7749, -122.4194),
    "seattle": (47.6062, -122.3321), "denver": (39.7392, -104.9903),
}

def _get_coords(city: str):
    key = city.lower().strip()
    # Try exact match first, then partial
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    for k, v in CITY_COORDS.items():
        if k in key or key in k:
            return v
    return None

def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def _estimate_flight_cost(origin: str, destination: str) -> dict:
    """
    Realistic flight cost estimation based on great-circle distance.
    Pricing tiers mirror real economy class averages:
      < 500 km  → $60–120   (short-haul domestic)
      500–2000  → $150–300  (medium-haul)
      2000–6000 → $350–600  (long-haul)
      > 6000 km → $600–1100 (ultra long-haul)
    """
    orig_coords = _get_coords(origin)
    dest_coords = _get_coords(destination)

    if not orig_coords or not dest_coords:
        # Unknown city — return a reasonable mid-range estimate
        return {"flight_cost": 450.0, "currency": "USD",
                "note": f"Estimated (city not in database). Origin: {origin}, Dest: {destination}"}

    dist_km = _haversine_km(*orig_coords, *dest_coords)

    if dist_km < 500:
        base = 80
        per_km = 0.12
    elif dist_km < 2000:
        base = 150
        per_km = 0.09
    elif dist_km < 6000:
        base = 300
        per_km = 0.055
    else:
        base = 550
        per_km = 0.035

    cost = round(base + (dist_km * per_km), 2)

    return {
        "flight_cost": cost,
        "currency": "USD",
        "distance_km": round(dist_km),
        "note": f"Estimated economy class fare ({origin} → {destination})"
    }

@tool
async def search_flights(origin: str, destination: str, departure_date: str) -> dict:
    """
    Estimates flight cost between two cities using distance-based pricing.
    No API key required. Returns realistic economy class fare estimates.
    """
    try:
        return _estimate_flight_cost(origin, destination)
    except Exception as e:
        return {"flight_cost": 400.0, "currency": "USD", "error": str(e)}