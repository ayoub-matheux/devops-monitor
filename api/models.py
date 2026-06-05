"""Pydantic schemas and Server dataclass."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


@dataclass
class Server:
    """Represents a monitored server."""

    id: str
    name: str
    host: str
    port: int
    status: Literal["unknown", "UP", "DEGRADED", "DOWN"] = "unknown"

    def base_url(self) -> str:
        """Return the base HTTP URL for this server."""
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Schema for registering a new server."""

    name: str = Field(..., min_length=1, description="Human-readable server name")
    host: str = Field(..., min_length=1, description="Hostname or IP address")
    port: int = Field(..., ge=1, le=65535, description="Port number (1–65535)")


class ServerOut(BaseModel):
    """Schema for server responses."""

    id: str
    name: str
    host: str
    port: int
    status: str

    class Config:
        from_attributes = True
