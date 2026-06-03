"""Background health-check poller."""

import asyncio
import logging
from typing import Dict

import httpx

from api.models import Server

logger = logging.getLogger(__name__)


async def poll_server(server_id: str, url: str, store: Dict[str, Server]) -> None:
    """Check the health of a single server and update its status in store.

    Args:
        server_id: The server's unique ID.
        url: The base URL of the server (e.g. http://host:port).
        store: The shared in-memory server dictionary.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                status = "UP"
            else:
                status = "DEGRADED"
    except Exception:
        status = "DOWN"

    if server_id in store:
        store[server_id].status = status
        logger.info("Server %s → %s", server_id, status)


async def run_poll_loop(store: Dict[str, Server], interval: int = 10) -> None:
    """Continuously poll all registered servers in parallel.

    Args:
        store: The shared in-memory server dictionary.
        interval: Seconds between each poll cycle.
    """
    while True:
        if store:
            tasks = [
                poll_server(sid, server.base_url(), store)
                for sid, server in list(store.items())
            ]
            await asyncio.gather(*tasks)
        await asyncio.sleep(interval)
