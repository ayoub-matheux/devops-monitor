"""FastAPI application entry point."""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory store
servers: Dict[str, Server] = {}
poll_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the background poller on startup and cancel it on shutdown."""
    global poll_task
    poll_task = asyncio.create_task(run_poll_loop(servers))
    logger.info("Background poller started.")
    yield
    poll_task.cancel()
    try:
        await poll_task
    except asyncio.CancelledError:
        logger.info("Background poller stopped.")


app = FastAPI(title="DevOps Monitor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Public endpoints ──────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health() -> dict:
    """Return API health status."""
    return {"status": "ok"}


@app.get("/metrics", tags=["Metrics"])
async def metrics() -> dict:
    """Return a current snapshot of system metrics."""
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket) -> None:
    """Stream system metrics as JSON every second."""
    await websocket.accept()
    try:
        while True:
            data = get_system_metrics()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")


@app.get("/servers", tags=["Servers"])
async def list_servers(status: Optional[str] = None) -> list[ServerOut]:
    """List all registered servers, optionally filtered by status."""
    result = list(servers.values())
    if status:
        result = [s for s in result if s.status == status]
    return [ServerOut(id=s.id, name=s.name, host=s.host, port=s.port, status=s.status) for s in result]


@app.get("/servers/{server_id}", tags=["Servers"])
async def get_server(server_id: str) -> ServerOut:
    """Return a single server by ID or 404."""
    server = servers.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found.")
    return ServerOut(id=server.id, name=server.name, host=server.host, port=server.port, status=server.status)


@app.post("/servers/{server_id}/check", tags=["Servers"])
async def trigger_check(server_id: str) -> dict:
    """Trigger an immediate health check for a single server."""
    server = servers.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found.")
    asyncio.create_task(poll_server(server_id, server.base_url(), servers))
    return {"message": f"Health check triggered for {server.name}."}


# ── Protected endpoints ───────────────────────────────────────────────────────

@app.post("/servers", status_code=status.HTTP_201_CREATED, tags=["Servers"])
async def register_server(
    body: ServerIn,
    _: str = Depends(verify_api_key),
) -> ServerOut:
    """Register a new server. Requires API key."""
    server_id = str(uuid.uuid4())
    server = Server(id=server_id, name=body.name, host=body.host, port=body.port)
    servers[server_id] = server
    logger.info("Registered server %s (%s)", body.name, server_id)
    return ServerOut(id=server.id, name=server.name, host=server.host, port=server.port, status=server.status)


@app.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Servers"])
async def delete_server(
    server_id: str,
    _: str = Depends(verify_api_key),
) -> None:
    """Remove a server by ID. Requires API key."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found.")
    del servers[server_id]
    logger.info("Deleted server %s", server_id)
