from fastapi import APIRouter, BackgroundTasks, Depends
from ..models.fullerene import GenerateRequest, GenerateResponse
from ..core.generator import stream_generate
from ..core.cache import get_cache_instance

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def start_generation(req: GenerateRequest, tasks: BackgroundTasks, cache=Depends(get_cache_instance)):
    tasks.add_task(stream_generate, req.max_n, cache)
    return GenerateResponse(status="started", requested=req.max_n)
