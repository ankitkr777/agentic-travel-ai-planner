from langchain.tools import tool

@tool
async def search_hotels(destination: str, duration: int, budget: float) -> dict:
    """Searches for hotels for a specific duration and budget."""
    try:
        import asyncio; await asyncio.sleep(0.1)
        cost_per_night = (budget * 0.4) / max(duration, 1)
        return {"hotel_cost_total": budget * 0.4, "hotel_name": "Grand AI Hotel", "cost_per_night": cost_per_night}
    except Exception as e:
        return {"error": str(e)}