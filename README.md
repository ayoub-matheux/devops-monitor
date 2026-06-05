# DevOps Monitoring Dashboard

A real-time DevOps monitoring system built with FastAPI + Streamlit, containerized with Docker, and deployed on Azure via GitHub Actions CI/CD.

## Architecture

```
GitHub Actions CI/CD
  ├── lint (flake8)
  ├── test (pytest --cov ≥ 75%)
  ├── build & push → Azure Container Registry
  └── deploy → Azure Container Apps
       ├── devops-monitor-api       (FastAPI — port 8000)
       └── devops-monitor-dashboard (Streamlit — port 8501)
```

## Prerequisites

- Python 3.11
- Docker & Docker Compose
- Make

## Quick Start (< 5 minutes)

```bash
git clone https://github.com/<your-username>/devops-monitor.git
cd devops-monitor

cp .env.example .env    # fill in API_KEY value
make up                 # starts the full stack
make test               # runs tests
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_KEY` | API access key for protected endpoints | `my-secret-key` |
| `API_BASE` | API URL as seen by the dashboard | `http://api:8000` (Docker) or `http://localhost:8000` (local) |

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make up` | Start full stack with Docker Compose |
| `make down` | Stop and remove containers |
| `make logs` | Follow container logs |
| `make test` | Run tests with coverage >= 75% |
| `make lint` | Lint with flake8 |
| `make dev` | Run without Docker (local dev) |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | public | Health check |
| GET | `/metrics` | public | System metrics snapshot |
| WS | `/ws/metrics` | public | Live metrics stream |
| GET | `/servers` | public | List servers |
| POST | `/servers` | API key | Register a server |
| DELETE | `/servers/{id}` | API key | Remove a server |
| POST | `/servers/{id}/check` | public | Trigger health check |

## Live URLs (Azure)

> To be filled after Azure deployment.

- API: `https://<api>.<env>.azurecontainerapps.io/docs`
- Dashboard: `https://<dashboard>.<env>.azurecontainerapps.io`

## GitHub Secrets (CI/CD)

| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_CLIENT_SECRET` | App registration secret |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID |
| `ACR_NAME` | Container registry name (without `.azurecr.io`) |
| `API_KEY` | API key injected into Container Apps |
