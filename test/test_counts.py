from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import patch
from .mocks import MockAsyncProcess
from .testconstants import C30_INPUT, EXCEPTION_REASON
from app.main import app
from fastapi.testclient import TestClient
from app.core.cache import get_cache_instance
import pytest
from .base_integration_test import BaseIntegrationTest

class TestCount(BaseIntegrationTest):
    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenFullerenesGeneratedAndCountsCalled_shouldReturnRelevantCounts(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)

        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        
        wrapper = ProcessWrapper()

        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = client.get("/counts")

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "vertices": 30, 
                    "count": 1
                }
            ]
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenCountsCalledAndCacheFails_shouldReturnRelevantException(self, mock_create_subprocess_exec, sqlite_cache):

        self.useFaultyCache()
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = client.get("/counts")

        assert response.status_code == 500
        assert response.json() == {
            "detail": f"Failed to fetch counts due to {EXCEPTION_REASON}"
        }
        
        app.dependency_overrides = {}