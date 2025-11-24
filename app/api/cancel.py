from fastapi import APIRouter, BackgroundTasks, Depends
from ..models.fullerene import GenerateRequest, GenerateResponse
from ..core.generator import stream_generate
from ..core.cache import get_cache_instance
from ..states.job_state import ProcessWrapper
from generate import processWrapper


router = APIRouter()


@router.post("/cancel_generation", response_model=GenerateResponse)
async def start_generation():
    processWrapper.kill()
    return