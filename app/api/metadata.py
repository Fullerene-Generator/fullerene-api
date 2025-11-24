from fastapi import APIRouter, Depends
from ..core.cache import get_cache_instance
from ..models.fullerene import FullereneMetadataListResponse

router = APIRouter()

@router.get("/fullerenes/{size}", response_model=FullereneMetadataListResponse)
async def get_metadata(size: int, cache=Depends(get_cache_instance)):
    metadata = cache.get_metadata_for_size(size)
    return FullereneMetadataListResponse(
        size=size,
        count=len(metadata),
        metadata=metadata
    )
