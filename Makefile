lint:
	black . --check
	isort . --profile=black --check
	flake8
	mypy .

format:
	black .
	isort . --profile=black

build-web:  # Build backend web app image
	docker build -f docker/web.Dockerfile --tag bga-backend-web .

build-pipeline:  # Build pipeline job image
	docker build -f docker/pipeline.Dockerfile --tag bga-pipeline-job .

stack-pipeline-only: # Run only the pipeline container. Requires rest of stack to be up already
	docker compose -f docker/compose.yaml --project-name bga-backend run pipeline_job

stack-web-only:  # Run the stack without starting a data pipeline job
	docker compose -f docker/compose.yaml --project-name bga-backend up web db -d

stack-up:  # Run the full Docker compose stack
	docker compose -f docker/compose.yaml --project-name bga-backend up -d

stack-down:  # Destroy the Docker compose stack
	docker compose -f docker/compose.yaml --project-name bga-backend down

stack-logs:  # Follow the Docker compose logs
	docker compose -f docker/compose.yaml --project-name bga-backend logs --follow

stack-logs-pipeline:  # Follow the Docker logs for the pipeline container
	docker compose -f docker/compose.yaml --project-name bga-backend logs pipeline_job --follow