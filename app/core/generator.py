import asyncio
from .config import config
from .cache import Cache
from ..states.job_state import ProcessWrapper


async def stream_generate(max_n: int, cache: Cache, processWraper: ProcessWrapper):

    processWraper.setRunning()

    process = await asyncio.create_subprocess_exec(
        config.FULLERENE_EXE,
        str(max_n),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    processWraper.process = process
    reader = process.stdout

    current_id = 0

    while True:
        line = await reader.readline()
        if not line:
            break

        n = int(line.decode().strip())
        line = await reader.readline()
        outer_vertices = [int(x) for x in line.decode().split()]
        edges = []

        for _ in range(n):
            line = await reader.readline()
            u, v, w = line.decode().strip().split()
            edges.append([int(u), int(v), int(w)])

        cache.add_fullerene(n, current_id, outer_vertices, edges)
        current_id += 1

    await process.wait()
    processWraper.setIdle()
