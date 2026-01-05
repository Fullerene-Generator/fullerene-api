from fastapi import APIRouter, Depends, HTTPException
from ..core.cache import get_cache_instance
from ..models.fullerene import CountsResponse, CountPair
from typing import Optional

router = APIRouter()

@router.get("/counts", response_model=CountsResponse)
async def get_counts(is_ipr: Optional[bool] | None = None, cache=Depends(get_cache_instance)):
    try:
        counts = cache.get_counts(is_ipr)
    except Exception as e:
          raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch counts due to {e}"
        )
    items = [CountPair(vertices=size, count=count) for size, count in counts.items()]
    return CountsResponse(items=items)
