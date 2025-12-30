from fastapi import APIRouter, Depends, HTTPException
from ..core.cache import get_cache_instance
from ..models.fullerene import FullereneVisualizationData
import asyncio
from ..core.cache import Cache
from ..core.config import config
router = APIRouter()

@router.get("/fullerenes/2D/{size}/{id}", response_model=FullereneVisualizationData)
async def get_fullerene(size: int, id: str, cache: Cache=Depends(get_cache_instance)):
    try:
        data = cache.get_fullerene(size, id)
    except Exception as e:
        raise HTTPException(status_code = 500,
                            detail=f"Failed to fetch data for fullerene with id: {id}. Cause: {e}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Fullerene not found")
    
    process = await asyncio.create_subprocess_exec(
        config.EMBEDDER_2D_EXE,
        "2",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    lines = []

    lines.append(str(data["n"]))
    lines.append(" ".join(str(v) for v in data["outer_vertices"]))
    for e in data["edges"]:
        lines.append(" ".join(str(x) for x in e))

    input = "\n".join(lines)
    stdout, stderr = await process.communicate(input.encode())
    if stderr:
        raise HTTPException(status_code=500, detail=f"Error running 2D embedder due to : {stderr.decode()}")

    lines = stdout.decode().strip().splitlines()

    coords = []
    for line in lines:
        x, y = line.split()
        coords.append([float(x), float(y)])
    

    output_edges = []

    for i, neighbours in enumerate(data["edges"]):
        print(neighbours)
        for j in range(3):
            print(neighbours[j])
            if neighbours[j] > i:
                output_edges.append([int(i), int(neighbours[j])])

    
    return FullereneVisualizationData(id=id, n=size, edges=output_edges, coords=coords)


@router.get("/fullerenes/3D/{size}/{id}", response_model=FullereneVisualizationData)
async def get_fullerene(size: int, id: str, cache: Cache=Depends(get_cache_instance)):
    try:
        data = cache.get_fullerene(size, id)
    except Exception as e:
        raise HTTPException(status_code = 500,
                            detail=f"Failed to fetch data for fullerene with id: {id}. Cause: {e}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Fullerene not found")
    
    process = await asyncio.create_subprocess_exec(
        config.EMBEDDER_2D_EXE,
        "3",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    
    lines = []

    lines.append(str(data["n"]))
    lines.append(" ".join(str(v) for v in data["outer_vertices"]))
    for e in data["edges"]:
        lines.append(" ".join(str(x) for x in e))

    input = "\n".join(lines)
    stdout, stderr = await process.communicate(input.encode())
    if stderr:
        raise HTTPException(status_code=500, detail=f"Error running 3D embedder due to : {stderr.decode()}")

    lines = stdout.decode().strip().splitlines()

    coords = []
    for line in lines:
        x, y, z = line.split()
        coords.append([float(x), float(y), float(z)])
    

    output_edges = []

    for i, neighbours in enumerate(data["edges"]):
        for j in range(3):
            if neighbours[j] > i:
                output_edges.append([int(i), int(neighbours[j])])

    
    return FullereneVisualizationData(id=id, n=size, edges=output_edges, coords=coords)