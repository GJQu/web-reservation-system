.PHONY: setup run test lint seed docker-up docker-down migrate format

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	FLASK_APP=app flask run

test:
	python3 -m pytest tests/ -v

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

seed:
	python3 scripts/seed_data.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

migrate:
	FLASK_APP=app flask db migrate
	FLASK_APP=app flask db upgrade
