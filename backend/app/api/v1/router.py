from fastapi import APIRouter
from app.api.v1.endpoints import market

api_router = APIRouter()
api_router.include_router(market.router, prefix="/market", tags=["market"])