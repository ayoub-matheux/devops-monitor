include .env
export

PORT ?= 8000
IMAGE_NAME ?= devops-monitor
CONTAINER_NAME ?= devops-monitor-container

help:
	@echo "Available commands:"
	@echo "  make init          - Create virtualenv and install dependencies"
	@echo "  make dev           - Run API and dashboard locally (no Docker)"
	@echo "  make up            - Start full stack with Docker Compose"
	@echo "  make down          - Stop and remove containers"
	@echo "  make logs          - Follow container logs"
	@echo "  make build         - Build Docker images"
	@echo "  make test          - Run unit tests with coverage"
	@echo "  make lint          - Lint code with flake8"
	@echo "  make run           - Run API only on PORT (default: 8000)"
	@echo "  make run-container - Run API as a standalone Docker container"
	@echo "  make stop          - Stop the standalone container"
	@echo "  make clean         - Remove stopped containers"

init:
	python -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

dev:
	uvicorn api.main:app --reload --port $(PORT) &
	streamlit run dashboard/app.py

run:
	uvicorn api.main:app --reload --port $(PORT)

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

build:
	docker compose build

test:
	pytest tests/ -v --cov=api --cov-fail-under=75

lint:
	flake8 api/ dashboard/ tests/ --max-line-length=100

run-container:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):$(PORT) \
		--env-file .env \
		$(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)

clean:
	docker rm $$(docker ps -aq --filter "name=$(CONTAINER_NAME)")

.PHONY: help init dev run up down logs build test lint run-container stop clean
