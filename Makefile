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

run-pipeline-job: # Run only the pipeline container. Requires rest of stack to be up already
	docker compose -f docker/compose.yaml --project-name bga-backend run pipeline_job && \
 	docker compose -f docker/compose.yaml --project-name bga-backend logs pipeline_job -f

run-web-stack:  # Run the stack without starting a data pipeline job
	docker compose -f docker/compose.yaml --project-name bga-backend up web db -d

run-full-stack:  # Run the full Docker compose stack
	docker compose -f docker/compose.yaml --project-name bga-backend up -d \
	&& docker compose -f docker/compose.yaml --project-name bga-backend logs pipeline_job -f

stop-stack:  # Stop the Docker compose stack
	docker compose -f docker/compose.yaml --project-name bga-backend down

stack-logs:  # Follow the Docker compose logs
	docker compose -f docker/compose.yaml --project-name bga-backend logs -f