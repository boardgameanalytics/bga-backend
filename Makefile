poetry-init:
	poetry install --with all

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

build-pipeline:
	docker build -f docker/pipeline.Dockerfile --tag bga-pipeline-job

run-pipeline-job:
	docker compose run pipeline_job && docker compose logs pipeline_job

run-web-stack:
	docker compose up web db -d