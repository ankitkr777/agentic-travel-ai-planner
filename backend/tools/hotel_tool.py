from langchain.tools import tool

# Rough nightly hotel cost tiers by city category (USD, mid-range 3-star)
CITY_HOTEL_TIERS = {
    "expensive": {
        "cities": ["london", "new york", "nyc", "paris", "tokyo", "singapore",
                   "dubai", "sydney", "hong kong", "zurich", "geneva", "oslo"],
        "nightly_rate": 180,
        "hotel_name": "City Grand Hotel"
    },
    "moderate": {
        "cities": ["berlin", "amsterdam", "barcelona", "rome", "madrid", "vienna",
                   "prague", "lisbon", "athens", "toronto", "montreal", "seoul",
                   "bangkok", "istanbul", "miami", "los angeles", "la", "chicago",
                   "san francisco", "seattle"],
        "nightly_rate": 110,
        "hotel_name": "Comfort Suites"
    },
    "budget": {
        "cities": ["mumbai", "delhi", "beijing", "shanghai", "cairo", "nairobi",
                   "mexico city", "sao paulo", "buenos aires", "johannesburg",
                   "kolkata", "jakarta", "manila", "hanoi", "ho chi minh"],
        "nightly_rate": 55,
        "hotel_name": "Budget Inn & Suites"
    },
}

def _get_nightly_rate(destination: str) -> tuple[float, str]:
    dest_lower = destination.lower().strip()
    for tier, data in CITY_HOTEL_TIERS.items():
        if any(c in dest_lower or dest_lower in c for c in data["cities"]):
            return data["nightly_rate"], data["hotel_name"]
    # Unknown city — moderate default
    return 100, "Local Boutique Hotel"

@tool
async def search_hotels(destination: str, duration: int, budget: float) -> dict:
    """
    Returns a realistic hotel cost estimate for a destination based on city tier pricing.
    No API key required.
    """
    try:
        duration = max(duration, 1)
        nightly_rate, hotel_name = _get_nightly_rate(destination)

        # If budget is very tight, scale down to budget option
        max_affordable_nightly = (budget * 0.4) / duration
        if max_affordable_nightly < nightly_rate:
            nightly_rate = round(max_affordable_nightly, 2)
            hotel_name = "Budget-Friendly Stay"

        total_cost = round(nightly_rate * duration, 2)

        return {
            "hotel_cost_total": total_cost,
            "hotel_name": hotel_name,
            "cost_per_night": nightly_rate,
            "duration_nights": duration,
            "note": f"Estimated mid-range hotel in {destination}"
        }
    except Exception as e:
        fallback = round((budget * 0.4), 2)
        return {"hotel_cost_total": fallback, "hotel_name": "Local Hotel", "cost_per_night": round(fallback / max(duration, 1), 2), "error": str(e)}