from app.core.cache import SqliteCache
from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import AsyncMock, MagicMock, patch
from .mocks import MockAsyncProcess, FaultyCache
from .testconstants import C30_INPUT, C30_N, C30_EDGES, C30_OUTER_VERTICES
from app.main import app
from fastapi.testclient import TestClient
from app.core.cache import get_cache_instance
import pytest
import json
from .base_integration_test import BaseIntegrationTest

class TestGeneration(BaseIntegrationTest):
    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenAlgorithmGenerates_shouldSaveOutputInSqlite(self, mock_create_subprocess_exec, sqlite_cache):

        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        
        wrapper = ProcessWrapper()

        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        mock_create_subprocess_exec.assert_called_once()

        cur = sqlite_cache.conn.cursor()
        res = cur.execute("SELECT * FROM fullerenes")

        fullerene = res.fetchone()

        assert fullerene is not None

        _, n, outer_vertices_db, edges_json_db = fullerene
        
        assert n == C30_N
        assert json.loads(outer_vertices_db) == C30_OUTER_VERTICES
        assert json.loads(edges_json_db) == C30_EDGES
        assert wrapper.isRunning() == False


    @pytest.mark.asyncio
    async def test_whenProvidedValueIsNan_shouldreturnRelevantException(self):
        client = TestClient(app)

        response = client.post("/generate", json={"max_n": 10})

        assert response.status_code == 500
        assert response.json() == {
            "detail": "provided value has to be less or equal 20. Value: 10"
        }

