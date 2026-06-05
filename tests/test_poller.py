import asyncio

import pytest

from api.models import Server
from api.poller import poll_server, run_poll_loop


class DummyResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code


class DummyClientOK:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        return DummyResponse(status_code=200)


class DummyClientFail:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        return DummyResponse(status_code=500)


class DummyClientError:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        raise RuntimeError("connection failed")


@pytest.mark.asyncio
async def test_poll_server_sets_status_up(monkeypatch):
    store = {
        "server-1": Server(id="server-1", name="test", host="localhost", port=8000)
    }

    monkeypatch.setattr("api.poller.httpx.AsyncClient", DummyClientOK)

    await poll_server("server-1", "http://localhost:8000", store)

    assert store["server-1"].status == "UP"


@pytest.mark.asyncio
async def test_poll_server_sets_status_degraded(monkeypatch):
    store = {
        "server-2": Server(id="server-2", name="test", host="localhost", port=8001)
    }

    monkeypatch.setattr("api.poller.httpx.AsyncClient", DummyClientFail)

    await poll_server("server-2", "http://localhost:8001", store)

    assert store["server-2"].status == "DEGRADED"


@pytest.mark.asyncio
async def test_poll_server_sets_status_down_on_exception(monkeypatch):
    store = {
        "server-3": Server(id="server-3", name="test", host="localhost", port=8002)
    }

    monkeypatch.setattr("api.poller.httpx.AsyncClient", DummyClientError)

    await poll_server("server-3", "http://localhost:8002", store)

    assert store["server-3"].status == "DOWN"


@pytest.mark.asyncio
async def test_run_poll_loop_calls_poll_server(monkeypatch):
    store = {
        "server-4": Server(id="server-4", name="test", host="localhost", port=8003)
    }
    called = {"flag": False}

    async def fake_poll(server_id: str, url: str, store_arg):
        called["flag"] = True
        assert server_id == "server-4"
        assert url == "http://localhost:8003"
        assert store_arg is store

    async def fake_sleep(interval: int):
        raise asyncio.CancelledError

    monkeypatch.setattr("api.poller.poll_server", fake_poll)
    monkeypatch.setattr("api.poller.asyncio.sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await run_poll_loop(store, interval=0)

    assert called["flag"] is True
