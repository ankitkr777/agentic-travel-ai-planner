from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from backend.core.config import get_settings
from backend.tools.flight_tool import search_flights
from backend.tools.hotel_tool import search_hotels
from backend.tools.weather_tool import get_weather
from backend.tools.budget_tool import calculate_optimal_budget
from backend.tools.attraction_tool import search_attractions
from backend.rag.vector_store import get_vector_retriever
from backend.core.logging import logger
import json

settings = get_settings()

# GROK INTEGRATION
llm = ChatOpenAI(
    model="grok-beta",
    base_url="https://api.x.ai/v1",
    api_key=settings.XAI_API_KEY,
    temperature=settings.OPENAI_TEMPERATURE
)

class PlannerState(TypedDict):
    destination: str
    origin: str
    duration: int
    budget: float
    departure_date: str
    raw_preferences: str
    flight_data: dict
    hotel_data: dict
    weather_data: dict
    budget_data: dict
    attractions: list
    rag_context: str
    final_plan: dict

async def extract_requirements(state: PlannerState) -> PlannerState:
    try:
        logger.info("Agent: Extracting requirements via Grok...")
        prompt = f"""Extract these from the query: destination (city name), origin (city name, default 'NYC'), duration (days), budget (number), departure_date (YYYY-MM-DD format, use a date 2 weeks from now if missing).
        Return ONLY valid JSON: {{"destination": "string", "origin": "string", "duration": int, "budget": float, "departure_date": "string"}}
        Query: {state['raw_preferences']}"""
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        data = json.loads(response.content)
        state["destination"] = data.get("destination", "Paris")
        state["origin"] = data.get("origin", "NYC")
        state["duration"] = data.get("duration", 3)
        state["budget"] = data.get("budget", 1000.0)
        state["departure_date"] = data.get("departure_date", "2024-12-15")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        state["destination"], state["origin"], state["duration"], state["budget"] = "Paris", "NYC", 3, 1000.0
        state["departure_date"] = "2024-12-15"
    return state

async def fetch_data_tools(state: PlannerState) -> PlannerState:
    try:
        logger.info("Agent: Executing REAL API calls (Amadeus + Open-Meteo)...")
        dest, orig, dur, bud, dep_date = state["destination"], state["origin"], state["duration"], state["budget"], state["departure_date"]
        
        state["flight_data"] = await search_flights.ainvoke({"origin": orig, "destination": dest, "departure_date": dep_date})
        state["weather_data"] = await get_weather.ainvoke({"destination": dest})
        state["hotel_data"] = await search_hotels.ainvoke({"destination": dest, "duration": dur, "budget": bud})
        state["budget_data"] = await calculate_optimal_budget.ainvoke({"total_budget": bud})
        state["attractions"] = await search_attractions.ainvoke({"destination": dest})
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
    return state

async def fetch_rag_context(state: PlannerState) -> PlannerState:
    try:
        logger.info("Agent: Fetching RAG context (Local HuggingFace)...")
        retriever = get_vector_retriever()
        if retriever:
            docs = await retriever.ainvoke(f"Travel tips for {state['destination']}")
            state["rag_context"] = " ".join([d.page_content for d in docs])
        else:
            state["rag_context"] = "No RAG context."
    except Exception as e:
        logger.error(f"RAG fetch failed: {e}")
        state["rag_context"] = ""
    return state

async def synthesize_final_plan(state: PlannerState) -> PlannerState:
    try:
        logger.info("Agent: Synthesizing plan via Grok...")
        prompt = f"""Create a travel plan. You MUST output ONLY valid JSON: {{"destination": string, "duration": int, "budget": float, "itinerary": [{{"day": int, "activities": [string]}}], "cost_breakdown": {{"flights": float, "hotel": float, "food": float, "activities": float, "misc": float}}, "tips": [string], "recommendations": [string]}}
        Context: Destination: {state['destination']}, Duration: {state['duration']} days. 
        REAL FLIGHT DATA: {state['flight_data']}. 
        REAL WEATHER DATA: {state['weather_data']}. 
        Hotel Data: {state['hotel_data']}, Budget Allocation: {state['budget_data']}, Attractions: {state['attractions']}, RAG Tips: {state['rag_context']}
        
        IMPORTANT: If the flight data contains an error or price is 0, estimate the flight cost based on the budget. If weather data has an error, estimate average weather."""
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        state["final_plan"] = json.loads(clean_json)
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        state["final_plan"] = {"error": "Failed to generate plan"}
    return state

def build_planner_graph():
    workflow = StateGraph(PlannerState)
    workflow.add_node("extract", extract_requirements)
    workflow.add_node("tools", fetch_data_tools)
    workflow.add_node("rag", fetch_rag_context)
    workflow.add_node("synthesize", synthesize_final_plan)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "tools")
    workflow.add_edge("tools", "rag")
    workflow.add_edge("rag", "synthesize")
    workflow.add_edge("synthesize", END)
    return workflow.compile()