from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import patch
from .mocks import MockAsyncProcess, FaultyCache
from .testconstants import C30_INPUT, EXCEPTION_REASON, C60_INPUT, C60_IPR_INPUT
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
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=(C60_INPUT + "\n" + C60_IPR_INPUT))
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = client.get("/fullerenes/60?limit=10&offset=0")

        assert response.status_code == 200
        assert response.json() == {
            "size": 60,
            "count": 2,
            "metadata": [
                {
                    "id": "60:0",
                    "n": 60,
                    "parent_id": "50:0",
                    "is_ipr": False,
                },
                {
                    "id": "60:1661",
                    "n": 60,
                    "parent_id": "60:50",
                    "is_ipr": True,
                }
            ]
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenLimitSmallerThanCountOfGraohs_shouldReturnDataForEquivalentPage(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=(C60_INPUT + "\n" + C60_IPR_INPUT))
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response1 = client.get("/fullerenes/60?limit=1&offset=0")

        response2=  client.get("/fullerenes/60?limit=1&offset=1")

        assert response1.status_code == 200
        assert response2.status_code == 200

        assert response1.json() == {
            "size": 60,
            "count": 1,
            "metadata": [
                {
                    "id": "60:0",
                    "n": 60,
                    "parent_id": "50:0",
                    "is_ipr": False,
                }
            ]
        }

        assert response2.json() == {
            "size": 60,
            "count": 1,
            "metadata": [
                {
                    "id": "60:1661",
                    "n": 60,
                    "parent_id": "60:50",
                    "is_ipr": True,
                }
            ]
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenMetadataForIprExists_shouldReturnRelevantMetadata(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=(C60_INPUT + "\n" + C60_IPR_INPUT))
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = response = client.get("/fullerenes/60?limit=10&offset=0&is_ipr=true")

        assert response.status_code == 200
        assert response.json() == {
            "size": 60,
            "count": 1,
            "metadata": [
                {
                "id": "60:1661",
                "n": 60,
                "parent_id": "60:50",
                "is_ipr": True,
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

        response = client.get("/fullerenes/30?limit=10&offset=0")

        assert response.status_code == 500
        assert response.json() == {
        "detail" : f"Cannot fetch metadata for size 30. Cause: {EXCEPTION_REASON}"
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenNoMetadataForGivenSize_should404NotFound(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)

        response = client.get("/fullerenes/30?limit=10&offset=0")

        assert response.status_code == 404
        assert response.json() == {
            "detail" : "Metadata for given size not found size: 30"
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenNoMetadataForGivenIpr_should404NotFound(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = response = client.get("/fullerenes/30?limit=10&offset=0&is_ipr=true")

        assert response.status_code == 404
        assert response.json() == {
            "detail" : "Metadata for given size not found size: 30"
        }
        
        app.dependency_overrides = {}

# metadata by ID

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenMetadataForRequestedIdExists_shouldReturnRelevantMetadata(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = response = client.get("/fullerenes/ID/30:0")

        assert response.status_code == 200
        assert response.json() == {
            "metadata": 
                {
                "id": "30:0",
                "n": 30,
                "parent_id": "BASE",
                "is_ipr": False,
                }
        }
        
        app.dependency_overrides = {}


    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenNoMetadataForRequestedId_should404NotFound(self, mock_create_subprocess_exec, sqlite_cache):

        app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache
        client = TestClient(app)

        response = response = client.get("/fullerenes/ID/30:0")

        assert response.status_code == 404
        assert response.json() == {
            "detail" : "Metadata for given id not found id: 30:0"
        }
        
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('app.core.generator.asyncio.create_subprocess_exec')
    async def test_whenFaultyCacheForRequestedId_shouldReturnRelevantError(self, mock_create_subprocess_exec, sqlite_cache):

        self.useFaultyCache()
        client = TestClient(app)
        mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
        wrapper = ProcessWrapper()
        await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

        response = response = client.get("/fullerenes/ID/30:0")

        assert response.status_code == 500
        assert response.json() == {
        "detail" : f"Cannot fetch metadata for id 30:0. Cause: {EXCEPTION_REASON}"
        }
        
        app.dependency_overrides = {}
