.PHONY: dev dev-bg stop install backend-install frontend-install migrate migrate-new test test-backend test-frontend test-integration lint lint-backend lint-frontend seed clean

# ---------- Docker ----------
dev:
	docker-compose up

dev-bg:
	docker-compose up -d

stop:
	docker-compose down

# ---------- Install ----------
backend-install:
	cd backend && uv sync

frontend-install:
	cd frontend && pnpm install

install: backend-install frontend-install

# ---------- Migrations ----------
migrate:
	cd backend && uv run alembic upgrade head

migrate-new:
	cd backend && uv run alembic revision --autogenerate -m "$(name)"

# ---------- Tests ----------
test-backend:
	cd backend && uv run pytest tests/ -v

test-frontend:
	cd frontend && pnpm test

test-integration:
	cd backend && uv run pytest tests/integration/ -v

test: test-backend test-frontend

# ---------- Lint / Format ----------
lint-backend:
	cd backend && uv run ruff check app/ && uv run ruff format --check app/

lint-frontend:
	cd frontend && pnpm biome check --write src

lint: lint-backend lint-frontend

# ---------- Seed ----------
seed:
	cd backend && uv run python scripts/seed-workflow.py

# ---------- Clean ----------
clean:
	docker-compose down -v
	find backend -type d -name __pycache__ -exec rm -rf {} +
	rm -rf frontend/node_modules frontend/dist
