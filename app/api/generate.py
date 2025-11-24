from fastapi import APIRouter, BackgroundTasks, Depends
from ..models.fullerene import GenerateRequest, GenerateResponse
from ..core.generator import stream_generate
from ..core.cache import get_cache_instance
from ..states.job_state import ProcessWrapper
import subprocess
import threading

from enum import Enum


router = APIRouter()

processWrapper = ProcessWrapper()

@router.post("/generate", response_model=GenerateResponse)
async def start_generation(req: GenerateRequest, tasks: BackgroundTasks, cache=Depends(get_cache_instance)):
    tasks.add_task(stream_generate, req.max_n, cache, processWrapper)
    return GenerateResponse(status="started", requested=req.max_n)

@router.get("/isGenerating", response_model=bool)
async def start_generation():
    return processWrapper.isRunning()

@router.post("/cancel_generation")
async def start_generation():
    processWrapper.kill()
    return