from pydantic import BaseModel
from typing import List

class FullereneMetadata(BaseModel):
    id: str
    parent_id: str
    n: int
    is_ipr: bool

class FullereneData(FullereneMetadata):
    edges: List[List[int]]

class FullereneVisualizationData(BaseModel):
    id: str
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

class FullereneMetadataByIdResponse(BaseModel):
    metadata: FullereneMetadata

