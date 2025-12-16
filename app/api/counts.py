from fastapi import APIRouter, Depends, HTTPException
from ..core.cache import get_cache_instance
from ..models.fullerene import CountsResponse, CountPair

router = APIRouter()

@router.get("/counts", response_model=CountsResponse)
async def get_counts(cache=Depends(get_cache_instance)):
    try:
        counts = cache.get_counts()
    except Exception:
          raise HTTPException(
            status_code=500,
            detail="Failed to fetch counts"
        )
    items = [CountPair(vertices=size, count=count) for size, count in counts.items()]
    return CountsResponse(items=items)
