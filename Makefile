init:
	poetry install --with web,pipeline,dev

lint:
	black . --check
	isort . --profile=black --check
	flake8
	mypy .

format:
	black .
	isort . --profile=black

build-web:
	docker build -f docker/web.Dockerfile --tag bga-backend-web .

docker-up:
	docker compose -f compose.yaml up -d

docker-all-logs:
	docker compose logs

docker-down:
	docker compose down