from langchain.tools import tool
import httpx

@tool
async def get_weather(destination: str) -> dict:
    """Gets REAL current weather for a destination city using Open-Meteo (No API key needed)."""
    try:
        async with httpx.AsyncClient() as client:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1"
            geo_resp = await client.get(geo_url)
            geo_data = geo_resp.json()
            
            if not geo_data.get("results"):
                return {"error": "City not found"}
            
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = await client.get(weather_url)
            weather_data = weather_resp.json()["current_weather"]
            
            return {
                "temperature_c": weather_data["temperature"],
                "wind_speed": weather_data["windspeed"],
                "conditions": "Clear" if weather_data["weathercode"] == 0 else "Variable"
            }
    except Exception as e:
        return {"error": str(e)}