import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    FULLERENE_EXE = os.getenv("FULLERENE_EXE")
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory").lower()

config = Config()
