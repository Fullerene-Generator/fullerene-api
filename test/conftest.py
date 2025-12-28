import pytest
from app.core.cache import SqliteCache

@pytest.fixture
def sqlite_cache():
    cache = SqliteCache()
    yield cache
    cache.conn.close()