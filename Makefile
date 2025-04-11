### ---------------------------------------------------------------------------
### bga-backend Makefile Commands
### Stack refers to the Docker Compose stack defined in `docker/compose.yaml`.
### ---------------------------------------------------------------------------

# Pre-define the base Docker Compose command with file and project-name flags
DOCKER_COMPOSE_BASE_CMD = docker compose --file docker/compose.yaml --project-name bga-backend

CYAN ?= \033[0;36m
COFF ?= \033[0m

.DEFAULT: help
help:
	@sed -ne '/@sed/!s/### //p' $(MAKEFILE_LIST)  # Print help summary
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-30s$(COFF) %s\n", $$1, $$2}'

.PHONY: lint
lint:						## Run linters and type checkers
	black . --check
	isort . --profile=black --check
	flake8
	mypy .

.PHONY: format
format:						## Run code formatters
	black .
	isort . --profile=black

.PHONY: test
test:						## Run pytest suite
	pytest

.PHONY: stack-build
stack-build:				## Build the stack
	${DOCKER_COMPOSE_BASE_CMD} build

.PHONY: stack-up
stack-up:					## Run the full stack
	${DOCKER_COMPOSE_BASE_CMD} up -d

.PHONY: stack-stop
stack-stop:					## Stop the stack
	${DOCKER_COMPOSE_BASE_CMD} stop

.PHONY: stack-down
stack-down:					## Destroy the stack containers, keep persistent volumes
	${DOCKER_COMPOSE_BASE_CMD} down

.PHONY: stack-logs
stack-logs:					## Follow the stack logs
	${DOCKER_COMPOSE_BASE_CMD} logs --follow

.PHONY: stack-logs-pipeline
stack-logs-pipeline:		## Follow the logs for the pipeline container
	${DOCKER_COMPOSE_BASE_CMD} logs pipeline_job --follow

.PHONY: stack-web
stack-logs-web:				## Follow the logs for the pipeline container
	${DOCKER_COMPOSE_BASE_CMD} logs web --follow

.PHONY: stack-run-pipeline-only
stack-run-pipeline-only:	## Run only the pipeline container. Requires rest of stack to be up already
	${DOCKER_COMPOSE_BASE_CMD} up pipeline_job

.PHONY: stack-run-web-only
stack-run-web-only:			## Run the stack without starting a data pipeline job
	${DOCKER_COMPOSE_BASE_CMD} up web db -d
