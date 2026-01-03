from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import AsyncMock, patch
from .mocks import MockAsyncProcess, FaultyCache
from .testconstants import C30_INPUT, C30_EDGES_EMBEDDING, C30_2D_EMBEDDER_OUTPUT, C30_2D_EMBEDDING_OUTPUT, EXCEPTION_REASON
from app.main import app
from fastapi.testclient import TestClient
from app.core.cache import get_cache_instance
import pytest
from .base_integration_test import BaseIntegrationTest

class Test3DVisualization(BaseIntegrationTest):
    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    @patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
    async def test_whenFullereneGenerated_2DshouldReturn2DCoords(self, mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

        client = TestClient(app)
        process_instance = MockAsyncProcess(input=C30_INPUT)
        mock_create_subprocess_exec.return_value = process_instance

        wrapper = ProcessWrapper()

        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
        mock_embedder_subprocess_exec.return_value = process_instance
        response = client.get("/fullerenes/2D/30/30:0")
        process_instance.communicate.assert_awaited_once()

        
        assert response.status_code == 200
        assert response.json() == {
            "id": 0,
            "n": 30,
            "edges": C30_EDGES_EMBEDDING,
            "coords": C30_2D_EMBEDDING_OUTPUT
        }
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    @patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
    async def test_whenGetFullereneFails_2DshouldReturnRelevantException(self, mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

        self.useFaultyCache()

        client = TestClient(app)
        process_instance = MockAsyncProcess(input=C30_INPUT)
        mock_create_subprocess_exec.return_value = process_instance
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
        mock_embedder_subprocess_exec.return_value = process_instance
        response = client.get("/fullerenes/2D/30/30:0")

        
        assert response.status_code == 500
        assert response.json() == {
            "detail": f"Failed to fetch data for fullerene with id: 30:0. Cause: {EXCEPTION_REASON}"
        }
        app.dependency_overrides = {}


    @pytest.mark.asyncio
    @patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
    async def test_whenFullerneNotGenerated_2DshouldReturn404NotFound(self, mock_embedder_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

        client = TestClient(app)

        process_instance = MockAsyncProcess()
        process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
        mock_embedder_subprocess_exec.return_value = process_instance


        response = client.get("/fullerenes/2D/30/30:0")


        assert response.status_code == 404
        assert response.json() == {
            "detail": "Fullerene not found"
        }
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    @patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
    async def test_when2DEmbedderRespondsWithError_shouldRaiseRelevantException(self, mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

        client = TestClient(app)
        process_instance = MockAsyncProcess(input=C30_INPUT)
        mock_create_subprocess_exec.return_value = process_instance

        wrapper = ProcessWrapper()

        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        process_instance.communicate = AsyncMock(return_value=(None, EXCEPTION_REASON.encode()))
        mock_embedder_subprocess_exec.return_value = process_instance
        response = client.get("/fullerenes/2D/30/30:0")
        process_instance.communicate.assert_awaited_once()


        assert response.status_code == 500
        assert response.json() == {
            "detail": f"Error running 2D embedder due to : {EXCEPTION_REASON}"
        }
        app.dependency_overrides = {}