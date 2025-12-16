from app.core.cache import SqliteCache
from app.core.generator import stream_generate
from app.states.job_state import ProcessWrapper
from unittest.mock import AsyncMock, MagicMock, patch
from .mocks import MockAsyncProcess, FaultyCache
from .testconstants import C30_INPUT, C30_N, C30_EDGES, C30_OUTER_VERTICES, C30_3D_EMBEDDER_OUTPUT, C30_EDGES_EMBEDDING, C30_3D_EMBEDDING_OUTPUT, C30_2D_EMBEDDER_OUTPUT, C30_2D_EMBEDDING_OUTPUT
from app.main import app
from fastapi.testclient import TestClient
from app.core.cache import get_cache_instance
import pytest
import json

@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
async def test_whenAlgorithmGenerates_shouldSaveOutputInSqlite(mock_create_subprocess_exec, sqlite_cache):

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

    print(fullerene)


@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
async def test_whenFullerenesGeneratedAndCountsCalled_shouldReturnRelevantCounts(mock_create_subprocess_exec, sqlite_cache):

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
async def test_whenCountsCalledAndCacheFails_shouldReturnRelevantException(mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: FaultyCache()
    client = TestClient(app)
    mock_create_subprocess_exec.return_value = MockAsyncProcess(input=C30_INPUT)
    wrapper = ProcessWrapper()
    await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

    response = client.get("/counts")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to fetch counts"
    }
    
    app.dependency_overrides = {}

@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
async def test_whenFullerenesGeneratedAndMetadataCalled_shouldReturnRelevantMetadata(mock_create_subprocess_exec, sqlite_cache):

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
async def test_whenMetadataCalledAndCacheFaulty_shouldRaiseRelevantException(mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: FaultyCache()
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
async def test_whenNoMetadataForGivenSize_shouldReturnRelevantMetadata(mock_create_subprocess_exec, sqlite_cache):

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


@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
@patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
async def test_whenFullerneGenerated_shouldReturn3Dcoords(mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

    client = TestClient(app)
    process_instance = MockAsyncProcess(input=C30_INPUT)
    mock_create_subprocess_exec.return_value = process_instance

    wrapper = ProcessWrapper()

    await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

    process_instance.communicate = AsyncMock(return_value=(C30_3D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance
    response = client.get("/fullerenes/3D/30/0")
    process_instance.communicate.assert_awaited_once()


    assert response.status_code == 200
    assert response.json() == {
        "id": 0,
        "n": 30,
        "edges": C30_EDGES_EMBEDDING,
        "coords": C30_3D_EMBEDDING_OUTPUT
    }
    app.dependency_overrides = {}

@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
@patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
async def test_whenGetFullereneFails_shouldReturnRelevantException(mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: FaultyCache()

    client = TestClient(app)
    process_instance = MockAsyncProcess(input=C30_INPUT)
    mock_create_subprocess_exec.return_value = process_instance
    wrapper = ProcessWrapper()
    await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)
    process_instance.communicate = AsyncMock(return_value=(C30_3D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance
    response = client.get("/fullerenes/3D/30/0")


    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to fetch data for fullerene with id: 0. Cause: unknown exception"
    }
    app.dependency_overrides = {}

@pytest.mark.asyncio
@patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
async def test_whenFullerneNotGenerated_shouldReturn404NotFound(mock_embedder_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

    client = TestClient(app)

    process_instance = MockAsyncProcess()
    process_instance.communicate = AsyncMock(return_value=(C30_3D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance


    response = client.get("/fullerenes/3D/30/0")


    assert response.status_code == 404
    assert response.json() == {
        "detail": "Fullerene not found"
    }
    app.dependency_overrides = {}

@pytest.mark.asyncio
@patch('app.core.generator.asyncio.create_subprocess_exec')
@patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
async def test_whenFullereneGenerated_3DshouldReturn2DCoords(mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

    client = TestClient(app)
    process_instance = MockAsyncProcess(input=C30_INPUT)
    mock_create_subprocess_exec.return_value = process_instance

    wrapper = ProcessWrapper()

    await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

    process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance
    response = client.get("/fullerenes/2D/30/0")
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
async def test_whenGetFullereneFails_2DshouldReturnRelevantException(mock_embedder_subprocess_exec, mock_create_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: FaultyCache()
    client = TestClient(app)
    process_instance = MockAsyncProcess(input=C30_INPUT)
    mock_create_subprocess_exec.return_value = process_instance
    wrapper = ProcessWrapper()
    await stream_generate(max_n=10, cache=sqlite_cache, processWraper=wrapper)

    process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance
    response = client.get("/fullerenes/2D/30/0")

    
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to fetch data for fullerene with id: 0. Cause: unknown exception"
    }
    app.dependency_overrides = {}


@pytest.mark.asyncio
@patch('app.api.fullerene_data.asyncio.create_subprocess_exec')
async def test_whenFullerneNotGenerated_2DshouldReturn404NotFound(mock_embedder_subprocess_exec, sqlite_cache):

    app.dependency_overrides[get_cache_instance] = lambda: sqlite_cache

    client = TestClient(app)

    process_instance = MockAsyncProcess()
    process_instance.communicate = AsyncMock(return_value=(C30_2D_EMBEDDER_OUTPUT.encode(), None))
    mock_embedder_subprocess_exec.return_value = process_instance


    response = client.get("/fullerenes/2D/30/0")


    assert response.status_code == 404
    assert response.json() == {
        "detail": "Fullerene not found"
    }
    app.dependency_overrides = {}