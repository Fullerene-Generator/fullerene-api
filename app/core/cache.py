from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypedDict
from threading import Lock
from app.core.config import config


class FullereneMetadataDict(TypedDict):
    id: int
    n: int


class FullereneDataDict(TypedDict):
    id: int
    n: int
    outer_vertices: List[int]
    edges: List[List[int]]


class Cache(ABC):
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def incr(self, key: str) -> int:
        pass

    @abstractmethod
    def keys(self) -> List[str]:
        pass

    @abstractmethod
    def add_fullerene(
        self,
        n: int,
        id: int,
        outer_vertices: List[int],
        edges: List[List[int]]
    ) -> None:
        pass

    @abstractmethod
    def get_counts(self) -> Dict[int, int]:
        pass

    @abstractmethod
    def get_metadata_for_size(self, n: int) -> List[FullereneMetadataDict]:
        pass

    @abstractmethod
    def get_fullerene(self, n: int, id: int) -> Optional[FullereneDataDict]:
        pass


class MemoryCache(Cache):
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.lock = Lock()

    def set(self, key: str, value: Any) -> None:
        with self.lock:
            self.store[key] = value

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            return self.store.get(key)

    def incr(self, key: str) -> int:
        with self.lock:
            new_val = self.store.get(key, 0) + 1
            self.store[key] = new_val
            return new_val

    def keys(self) -> List[str]:
        with self.lock:
            return list(self.store.keys())

    def add_fullerene(
        self,
        n: int,
        id: int,
        outer_vertices: List[int],
        edges: List[List[int]],
    ) -> None:

        full_key = f"fullerene:{n}:{id}"
        meta_key = f"metadata:{n}:{id}"

        full_data: FullereneDataDict = {
            "id": id,
            "n": n,
            "outer_vertices": outer_vertices,
            "edges": edges,
        }

        meta_data: FullereneMetadataDict = {
            "id": id,
            "n": n
        }

        self.set(full_key, full_data)
        self.set(meta_key, meta_data)
        self.incr(f"count:{n}")

    def get_counts(self) -> Dict[int, int]:
        result: Dict[int, int] = {}

        for k in self.keys():
            if k.startswith("count:"):
                n = int(k.split(":")[1])
                count = self.get(k)
                if isinstance(count, int):
                    result[n] = count

        return result

    def get_metadata_for_size(self, n: int) -> List[FullereneMetadataDict]:
        prefix = f"metadata:{n}:"
        result: List[FullereneMetadataDict] = []

        for k in self.keys():
            if k.startswith(prefix):
                item = self.get(k)
                if isinstance(item, dict):
                    result.append(item)

        result.sort(key=lambda meta: meta["id"])
        return result

    def get_fullerene(self, n: int, id: int) -> Optional[FullereneDataDict]:
        value = self.get(f"fullerene:{n}:{id}")
        if isinstance(value, dict):
            return value
        return None


_cache_instance: Optional[Cache] = None


def get_cache_instance() -> Cache:
    global _cache_instance

    if _cache_instance is not None:
        return _cache_instance

    backend = config.CACHE_BACKEND

    if backend == "memory":
        _cache_instance = MemoryCache()

    else:
        raise ValueError(f"Unknown CACHE_BACKEND: {backend}")

    return _cache_instance