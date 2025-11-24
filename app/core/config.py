import os

class Config:
    FULLERENE_EXE = os.getenv("FULLERENE_EXE")
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory").lower()

config = Config()
