from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.schemas.schemas import TripCreate, TripResponse
from backend.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: AsyncSession = Depends(get_db)):
    try:
        service = TripService(db)
        return await service.create_trip(trip)
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = TripService(db)
        trip = await service.repo.get_trip(trip_id)
        if not trip: raise HTTPException(status_code=404, detail="Trip not found")
        return TripResponse.model_validate(trip)
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))