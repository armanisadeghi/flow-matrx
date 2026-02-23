.PHONY: dev test migrate lint install clean

dev:
	docker-compose up

dev-bg:
	docker-compose up -d

stop:
	docker-compose down

backend-install:
	cd backend && pip install -e ".[dev]"

frontend-install:
	cd frontend && npm install

install: backend-install frontend-install

migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate -m "$(name)"

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm run test

test: test-backend test-frontend

lint-backend:
	cd backend && ruff check app/ && ruff format --check app/

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

seed:
	cd backend && python scripts/seed-workflow.py

clean:
	docker-compose down -v
	find backend -type d -name __pycache__ -exec rm -rf {} +
	rm -rf frontend/node_modules frontend/dist
