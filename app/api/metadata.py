from fastapi import APIRouter, Depends, HTTPException
from ..core.cache import get_cache_instance
from ..models.fullerene import FullereneMetadataListResponse, FullereneMetadataByIdResponse

router = APIRouter()

@router.get("/fullerenes/{size}", response_model=FullereneMetadataListResponse)
async def get_metadata(size: int, cache=Depends(get_cache_instance)):
    try:
        metadata = cache.get_metadata_for_size(size)
    except Exception as e:
        raise HTTPException(status_code=500,
                             detail=f"Cannot fetch metadata for size {size}. Cause: {e}")

    if len(metadata) == 0:
         raise HTTPException(status_code=404, detail=f"Metadata for given size not found size: {size}")
    return FullereneMetadataListResponse(
        size=size,
        count=len(metadata),
        metadata=metadata
    )

@router.get("/fullerenes/ID/{id}", response_model=FullereneMetadataByIdResponse)
async def get_metadata_by_id(id: int, cache=Depends(get_cache_instance)):
    try:
        metadata = cache.get_metadata_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=500,
                             detail=f"Cannot fetch metadata for id {id}. Cause: {e}")

    if len(metadata) == 0:
         raise HTTPException(status_code=404, detail=f"Metadata for given id not found id: {id}")
    return FullereneMetadataByIdResponse(
        metadata=metadata
    )