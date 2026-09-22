install:
	pip install -r requirements.txt

test:
	pytest -q --cov=src/wafi --cov-report=term-missing

lint:
	ruff check src tests
	mypy src
	lint-imports

image:
	docker build -t wafi-ai .

smoke:
	docker compose up -d --build
	docker compose ps
	curl --fail http://localhost:8000/ready
	docker compose down
