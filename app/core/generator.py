import asyncio
from .config import config
from .cache import Cache
from ..states.job_state import ProcessWrapper


async def stream_generate(max_n: int, cache: Cache, processWraper: ProcessWrapper):

    processWraper.setRunning()

    cache.clear_cache()

    process = await asyncio.create_subprocess_exec(
        config.FULLERENE_EXE,
        str(max_n),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    processWraper.process = process
    reader = process.stdout

    while True:
        line = await reader.readline()
        if not line:
            break

        metadata_line = line.decode().strip().split()
        n, id, parent_id, is_ipr = metadata_line
        n: int = int(n)
        is_ipr: bool = (is_ipr == '1')

        line = await reader.readline()
        outer_vertices = [int(x) for x in line.decode().split()]
        edges = []

        for _ in range(n):
            line = await reader.readline()
            u, v, w = line.decode().strip().split()
            edges.append([int(u), int(v), int(w)])

        cache.add_fullerene(n, id, parent_id, is_ipr, outer_vertices, edges)

    await process.wait()
    processWraper.setIdle()
