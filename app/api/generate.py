from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from ..models.fullerene import GenerateRequest, GenerateResponse
from ..core.generator import stream_generate
from ..core.cache import get_cache_instance
from ..states.job_state import ProcessWrapper

from enum import Enum


router = APIRouter()

processWrapper = ProcessWrapper()


@router.post("/generate", response_model=GenerateResponse)
async def start_generation(req: GenerateRequest, tasks: BackgroundTasks, cache=Depends(get_cache_instance)):
    if req.max_n < 20:
        raise HTTPException(status_code=500, detail=f"provided value has to be less or equal 20. Value: {req.max_n}")
    tasks.add_task(stream_generate, req.max_n, cache, processWrapper)
    return GenerateResponse(status="started", requested=req.max_n)

@router.get("/isGenerating", response_model=bool)
async def start_generation():
    return processWrapper.isRunning()

@router.post("/cancel_generation")
async def start_generation():
    processWrapper.kill()
    return