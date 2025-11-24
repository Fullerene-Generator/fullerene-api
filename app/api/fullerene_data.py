from fastapi import APIRouter, Depends, HTTPException
from ..core.cache import get_cache_instance
from ..models.fullerene import FullereneDataResponse

router = APIRouter()

@router.get("/fullerenes/{size}/{id}", response_model=FullereneDataResponse)
async def get_fullerene(size: int, id: int, cache=Depends(get_cache_instance)):
    data = cache.get_fullerene(size, id)
    if not data:
        raise HTTPException(status_code=404, detail="Fullerene not found")
    return FullereneDataResponse(**data)
