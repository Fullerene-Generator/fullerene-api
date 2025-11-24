from fastapi import APIRouter, Depends
from ..core.cache import get_cache_instance
from ..models.fullerene import CountsResponse

router = APIRouter()

@router.get("/counts", response_model=CountsResponse)
async def get_counts(cache=Depends(get_cache_instance)):
    return CountsResponse(counts=cache.get_counts())
