from app.main import app
from app.core.cache import get_cache_instance
from .mocks import FaultyCache

class BaseIntegrationTest:
    def useFaultyCache(self):
        app.dependency_overrides[get_cache_instance] = lambda: FaultyCache()