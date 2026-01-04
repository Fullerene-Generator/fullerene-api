from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypedDict
from threading import Lock
from app.core.config import config
import sqlite3
import json

class FullereneMetadataDict(TypedDict):
    id: str
    n: int
    parent_id: str
    is_ipr: bool


class FullereneDataDict(TypedDict):
    id: str
    n: int
    parent_id: str
    is_ipr: bool
    outer_vertices: List[int]
    edges: List[List[int]]

class Cache(ABC):
    @abstractmethod
    def add_fullerene(
        self,
        n: int,
        id: str,
        parent_id: str,
        is_ipr: bool,
        outer_vertices: List[int],
        edges: List[List[int]]
    ) -> None:
        pass

    @abstractmethod
    def get_counts(self) -> Dict[int, int]:
        pass

    @abstractmethod
    def get_metadata_for_size(self, n: int, limit: int, offset: int) -> List[FullereneMetadataDict]:
        pass

    @abstractmethod
    def get_metadata_by_id(self, id: str) -> FullereneMetadataDict:
        pass

    @abstractmethod
    def get_fullerene(self, n: int, id: str) -> Optional[FullereneDataDict]:
        pass

    @abstractmethod
    def clear_cache(self):
        pass


class SqliteCache(Cache):
    def __init__(self):
        self.conn = initialize_db()

    def add_fullerene(
            self,
            n: int,
            id: str,
            parent_id: str,
            is_ipr: bool,
            outer_vertices: List[int],
            edges: List[List[int]]
    ):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO fullerenes(id, n, parent_id, is_ipr, outer_vertices, edges) VALUES (?, ?, ?, ?, ?, ?)",
                    (id, n, parent_id, is_ipr, json.dumps(outer_vertices), json.dumps(edges)))
        self.conn.commit()

    def get_counts(self):
        cur = self.conn.cursor()
        res = cur.execute("SELECT n, COUNT(*) FROM fullerenes GROUP BY n")
        result: Dict[int, int] = {}
        for row in res:
            result[row[0]] = row[1]
        return result

    def get_metadata_for_size(self, n, limit, offset):
        cur = self.conn.cursor()
        res = cur.execute("SELECT id, n, parent_id, is_ipr FROM fullerenes WHERE n=? LIMIT ? OFFSET ?", (n, limit, offset))
        result: List[FullereneMetadataDict] = []
        for row in res:
            result.append({
                "id": row[0],
                "n": row[1],
                "parent_id": row[2],
                "is_ipr": row[3],
            })
        return result
    
    def get_metadata_by_id(self, id):
        cur = self.conn.cursor()
        res = cur.execute("SELECT id, n, parent_id, is_ipr FROM fullerenes WHERE id=?", (id,))
        metadata = res.fetchone()
        return{
            "id": metadata[0],
            "n": metadata[1],
            "parent_id": metadata[2],
            "is_ipr": metadata[3],
        }

    def get_fullerene(self, n, id):
        cur = self.conn.cursor()
        res = cur.execute("SELECT * FROM fullerenes WHERE id=?", (id,))
        fullerene = res.fetchone()
        if fullerene is None:
            return None
        return {
            "id": fullerene[0],
            "n": fullerene[1],
            "parent_id": fullerene[2],
            "is_ipr": fullerene[3],
            "outer_vertices": json.loads(fullerene[4]),
            "edges": json.loads(fullerene[5]),
        }
    
    def clear_cache(self):
        self.conn.close()
        self.conn = initialize_db()


_cache_instance: Optional[Cache] = None

def initialize_db():
    conn = sqlite3.connect("", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("CREATE TABLE fullerenes(id VARCHAR PRIMARY KEY, n INTEGER, parent_id VARCHAR, is_ipr BIT, outer_vertices TEXT, edges TEXT)")
    return conn


def get_cache_instance() -> Cache:
    global _cache_instance

    if _cache_instance is not None:
        return _cache_instance

    backend = config.CACHE_BACKEND

    if backend == "sqlite":
         _cache_instance = SqliteCache()

    else:
        raise ValueError(f"Unknown CACHE_BACKEND: {backend}")

    return _cache_instance