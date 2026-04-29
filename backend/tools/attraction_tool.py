from langchain.tools import tool
import random

@tool
async def search_attractions(destination: str) -> list:
    """Finds top attractions at a destination."""
    try:
        import asyncio; await asyncio.sleep(0.1)
        attractions = [f"{destination} Tower", f"{destination} Museum", "Central Park", "Local Market"]
        return random.sample(attractions, 3)
    except Exception as e:
        return [{"error": str(e)}]