import os
from dotenv import load_dotenv

# odkomentuj jezeli włączasz aplikację lokalnie
load_dotenv()

class Config:
    FULLERENE_EXE = os.getenv("FULLERENE_EXE")
    EMBEDDER_2D_EXE = os.getenv("EMBEDDER_2D_EXE")
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory").lower()

config = Config()
