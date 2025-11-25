from fastapi import APIRouter, Depends
from ..core.cache import get_cache_instance
from ..models.fullerene import CountsResponse, CountPair

router = APIRouter()

@router.get("/counts", response_model=CountsResponse)
async def get_counts(cache=Depends(get_cache_instance)):
    counts = cache.get_counts()
    items = [CountPair(vertices=size, count=count) for size, count in counts.items()]
    return CountsResponse(items=items)
