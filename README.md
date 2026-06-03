# DevOps Monitor

A real-time DevOps Monitoring Dashboard built with FastAPI + Streamlit.

## Structure

```
devops-monitor/
├── api/
│   ├── main.py       # FastAPI app (routes, WebSocket, lifespan)
│   ├── metrics.py    # psutil helper
│   ├── auth.py       # API key dependency
│   ├── models.py     # Pydantic schemas + Server dataclass
│   └── poller.py     # Background health-check loop
├── dashboard/
│   └── app.py        # Streamlit frontend
├── tests/
│   ├── test_metrics.py
│   └── test_routes.py
├── requirements.txt
└── README.md
```

## Local Setup

```bash
# 1. Create and activate venv
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set API key
export API_KEY=my-secret-key  # Windows: set API_KEY=my-secret-key
```

## Running

**Terminal 1 — API:**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Dashboard:**
```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | public | Health check |
| GET | `/metrics` | public | System metrics snapshot |
| WS | `/ws/metrics` | public | Live metrics stream |
| GET | `/servers` | public | List servers (`?status=UP`) |
| GET | `/servers/{id}` | public | Get one server |
| POST | `/servers` | API key | Register a server |
| DELETE | `/servers/{id}` | API key | Remove a server |
| POST | `/servers/{id}/check` | public | Trigger health check |

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=api --cov-report=term-missing
```
