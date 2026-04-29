from fastapi import APIRouter, Depends, HTTPException
from backend.services.chat_service import ChatService
from backend.schemas.schemas import ChatRequest, TravelPlanResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_chat_service() -> ChatService: return ChatService()

@router.post("/plan", response_model=TravelPlanResponse)
async def generate_plan(request: ChatRequest, service: ChatService = Depends(get_chat_service)):
    try:
        plan = await service.process_message(request.message, request.user_id)
        return plan
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e: raise HTTPException(status_code=500, detail=str(e))