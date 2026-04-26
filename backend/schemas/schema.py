from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserResponse(BaseModel):
    id: int
    username: str
    preferences: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- TRIP SCHEMAS ---
class TripCreate(BaseModel):
    user_id: int
    destination: str = Field(..., min_length=1)
    duration_days: int = Field(..., gt=0)
    budget: float = Field(..., gt=0)

class TripResponse(BaseModel):
    id: int
    user_id: int
    destination: str
    duration_days: int
    budget: float
    final_plan_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- CHAT & AI SCHEMAS ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: int = Field(..., gt=0)

# STRICT STRUCTURED OUTPUT REQUIRED BY PROMPT
class TravelPlanResponse(BaseModel):
    destination: str
    duration: int
    budget: float
    itinerary: List[Dict[str, Any]]
    cost_breakdown: Dict[str, float]
    tips: List[str]
    recommendations: List[str]