from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import patch
from .mocks import MockAsyncProcess, FaultyCache
from .testconstants import C30_INPUT
from app.main import app
from fastapi.testclient import TestClient
from app.core.cache import get_cache_instance
import pytest
from .base_integration_test import BaseIntegrationTest

class TestMetadata(BaseIntegrationTest):
    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenFullerenesGeneratedAndMetadataCalled_shouldReturnRelevantMetadata(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = client.get("/fullerenes/30")

        assert response.status_code == 200
        assert response.json() == {
            "size": 30,
            "count": 1,
            "metadata": [
                {
                "id": 0,
                "n": 30
                }
            ]
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenMetadataCalledAndCacheFaulty_shouldRaiseRelevantException(self, mock_create_subprocess_exec, sqlite_cache):

        self.useFaultyCache()
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)
        response = client.get("/fullerenes/30")

        assert response.status_code == 500
        assert response.json() == {
        "detail" : "Cannot fetch metadata for size 30. Cause: unknown exception"
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenNoMetadataForGivenSize_shouldReturnRelevantMetadata(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)

        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        
        wrapper = ProcessWrapper()

        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = client.get("/fullerenes/20")

        assert response.status_code == 404
        assert response.json() == {
            "detail" : "Metadata for given size not found size: 20"
        }
        
        app.dependency_overrides = {}
