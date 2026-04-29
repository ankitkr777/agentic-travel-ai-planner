from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.trip_repository import TripRepository
from backend.schemas.schemas import TripCreate, TripResponse
from backend.core.logging import logger

class TripService:
    def __init__(self, db: AsyncSession): self.repo = TripRepository(db)

    async def create_trip(self, trip: TripCreate) -> TripResponse:
        try:
            db_trip = await self.repo.create_trip(trip)
            return TripResponse.model_validate(db_trip)
        except Exception as e:
            logger.error(f"Service Error creating trip: {e}")
            raise

    async def save_agent_plan(self, trip_id: int, plan_dict: dict) -> TripResponse:
        try:
            db_trip = await self.repo.update_plan(trip_id, plan_dict)
            return TripResponse.model_validate(db_trip)
        except Exception as e:
            logger.error(f"Service Error saving plan: {e}")
            raise