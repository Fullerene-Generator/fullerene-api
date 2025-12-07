from pydantic import BaseModel
from typing import List, Dict


class FullereneMetadata(BaseModel):
    id: int
    n: int


class FullereneData(BaseModel):
    id: int
    n: int
    edges: List[List[int]]

class FullereneVisualizationData(BaseModel):
    id: int
    n: int
    edges: List[List[int]]
    coords: List[List[float]]


class GenerateRequest(BaseModel):
    max_n: int


class GenerateResponse(BaseModel):
    status: str
    requested: int
    


class CountPair(BaseModel):
    vertices: int
    count: int


class CountsResponse(BaseModel):
    items: List[CountPair]


class FullereneMetadataListResponse(BaseModel):
    size: int
    count: int
    metadata: List[FullereneMetadata]

