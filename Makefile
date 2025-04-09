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

build-pipeline:
	docker build -f docker/pipeline.Dockerfile --tag bga-pipeline-job

run-pipeline-job:
	docker run --env-file=.env --volume=${PWD}/data:/data --name=bga-pipeline-job bga-pipeline-job

docker-up:
	docker compose -f compose.yaml up -d

docker-all-logs:
	docker compose logs

docker-down:
	docker compose down