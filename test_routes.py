"""Route tests using FastAPI TestClient."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
VALID_KEY = "dev-secret-key"
AUTH = {"X-API-Key": VALID_KEY}


def test_health():
    """GET /health returns 200 with status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics():
    """GET /metrics returns 200 and includes cpu_percent."""
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "cpu_percent" in data


def test_post_server_no_key():
    """POST /servers without API key returns 403."""
    resp = client.post("/servers", json={"name": "test", "host": "localhost", "port": 9000})
    assert resp.status_code == 403


def test_post_server_with_key():
    """POST /servers with valid key returns 201 and server appears in GET /servers."""
    resp = client.post(
        "/servers",
        json={"name": "test-server", "host": "localhost", "port": 9000},
        headers=AUTH,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-server"
    assert data["status"] == "unknown"

    # Server must appear in the list
    list_resp = client.get("/servers")
    assert list_resp.status_code == 200
    ids = [s["id"] for s in list_resp.json()]
    assert data["id"] in ids


def test_get_server_not_found():
    """GET /servers/{nonexistent_id} returns 404."""
    resp = client.get("/servers/nonexistent-id-12345")
    assert resp.status_code == 404


def test_delete_server():
    """DELETE /servers/{id} removes the server."""
    # Create one first
    create_resp = client.post(
        "/servers",
        json={"name": "to-delete", "host": "localhost", "port": 7777},
        headers=AUTH,
    )
    server_id = create_resp.json()["id"]

    # Delete it
    del_resp = client.delete(f"/servers/{server_id}", headers=AUTH)
    assert del_resp.status_code == 204

    # Should be gone
    get_resp = client.get(f"/servers/{server_id}")
    assert get_resp.status_code == 404


def test_port_validation():
    """POST /servers with invalid port returns 422."""
    resp = client.post(
        "/servers",
        json={"name": "bad-port", "host": "localhost", "port": 99999},
        headers=AUTH,
    )
    assert resp.status_code == 422
