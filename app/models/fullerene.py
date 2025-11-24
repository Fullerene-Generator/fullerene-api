from pydantic import BaseModel
from typing import List, Dict


class FullereneMetadata(BaseModel):
    id: int
    n: int


class FullereneData(BaseModel):
    id: int
    n: int
    edges: List[List[int]]
    coords: List[List[float]]


class GenerateRequest(BaseModel):
    max_n: int


class GenerateResponse(BaseModel):
    status: str
    requested: int


class CountsResponse(BaseModel):
    counts: Dict[int, int]  # { size: count }


class FullereneMetadataListResponse(BaseModel):
    size: int
    count: int
    metadata: List[FullereneMetadata]


class FullereneDataResponse(FullereneData):
    pass
