import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import generate, counts, metadata, fullerene_data

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Fullerene Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(counts.router)
app.include_router(metadata.router)
app.include_router(fullerene_data.router)