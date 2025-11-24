import asyncio
from .config import config
from .cache import Cache


async def stream_generate(max_n: int, cache: Cache):
    process = await asyncio.create_subprocess_exec(
        config.FULLERENE_EXE,
        str(max_n),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    reader = process.stdout

    current_id = 0

    while True:
        line = await reader.readline()
        if not line:
            break

        n = int(line.decode().strip())

        edges = []
        edges_count = (n * 3) // 2

        for _ in range(edges_count):
            line = await reader.readline()
            u, v = line.decode().strip().split()
            edges.append([int(u), int(v)])

        coords = []
        for _ in range(n):
            line = await reader.readline()
            x, y = line.decode().strip().split()
            coords.append([float(x), float(y)])

        cache.add_fullerene(n, current_id, edges, coords)
        current_id += 1

    await process.wait()
