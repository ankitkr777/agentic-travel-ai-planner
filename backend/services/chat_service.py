from backend.agents.planner_agent import build_planner_graph
from backend.schemas.schemas import TravelPlanResponse
from backend.core.logging import logger
from pydantic import ValidationError

class ChatService:
    def __init__(self): self.graph = build_planner_graph()

    async def process_message(self, message: str, user_id: int) -> dict:
        try:
            logger.info(f"Processing chat for user {user_id}")
            initial_state = {
                "raw_preferences": message, "destination": "", "origin": "", "duration": 0, 
                "budget": 0.0, "departure_date": "", "flight_data": {}, "hotel_data": {}, 
                "weather_data": {}, "budget_data": {}, "attractions": [], "rag_context": "", "final_plan": {}
            }
            final_state = await self.graph.ainvoke(initial_state)
            raw_plan = final_state.get("final_plan", {})
            
            validated_plan = TravelPlanResponse(**raw_plan)
            return validated_plan.model_dump()
        except ValidationError as e:
            logger.error(f"LLM output failed schema validation: {e}")
            raise ValueError("The AI generated an invalid travel plan format.")
        except Exception as e:
            logger.error(f"Unexpected error in chat service: {e}")
            raise RuntimeError("An unexpected error occurred while planning your trip.")