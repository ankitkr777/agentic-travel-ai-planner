from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.models import Trip
from backend.schemas.schemas import TripCreate
from backend.utils.helpers import dict_to_json_string
from backend.core.logging import logger

class TripRepository:
    def __init__(self, db: AsyncSession): self.db = db

    async def create_trip(self, trip: TripCreate) -> Trip:
        try:
            db_trip = Trip(**trip.model_dump())
            self.db.add(db_trip)
            await self.db.flush()
            await self.db.refresh(db_trip)
            return db_trip
        except Exception as e:
            logger.error(f"Repo Error creating trip: {e}")
            raise

    async def get_trip(self, trip_id: int) -> Trip:
        try:
            result = await self.db.execute(select(Trip).where(Trip.id == trip_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Repo Error fetching trip {trip_id}: {e}")
            raise
    
    async def update_plan(self, trip_id: int, plan_dict: dict) -> Trip:
        try:
            trip = await self.get_trip(trip_id)
            if not trip: raise ValueError("Trip not found")
            # PRODUCTION: We now pass pure dict to JSONB column, SQLAlchemy handles it natively
            trip.final_plan_json = plan_dict 
            await self.db.flush()
            await self.db.refresh(trip)
            return trip
        except Exception as e:
            logger.error(f"Repo Error updating trip plan: {e}")
            raise