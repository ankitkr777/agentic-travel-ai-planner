from langchain.tools import tool
from amadeus import Client, ResponseError
from backend.core.config import get_settings
import asyncio

@tool
async def search_flights(origin: str, destination: str, departure_date: str) -> dict:
    """Searches for REAL flights using the Amadeus API. Requires 3-letter airport codes (e.g., JFK, LAX, CDG)."""
    try:
        settings = get_settings()
        amadeus = Client(
            client_id=settings.AMADEUS_CLIENT_ID,
            client_secret=settings.AMADEUS_CLIENT_SECRET
        )
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=1
            )
        )
        
        if response.data:
            price = float(response.data[0]['price']['total'])
            return {"flight_cost": price, "currency": response.data[0]['price']['currency']}
        return {"flight_cost": 0, "error": "No flights found"}
        
    except ResponseError as e:
        return {"error": f"Amadeus Error: Check API keys or airport codes."}
    except Exception as e:
        return {"error": str(e)}