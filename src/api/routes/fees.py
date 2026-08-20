from fastapi import APIRouter
from src.api.broadcast import get_fees

router = APIRouter()

@router.get("/fees")
async def get_fees_endpoint():
    fees = get_fees()
    return {"fees": fees}
