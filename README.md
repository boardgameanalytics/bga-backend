# BoardGameAnalytics Backend & Data Engineering Stack

## Overview

This repository hosts the backend and data engineering code for the BoardGameAnalytics stack. It uses Docker containers
to host the web backend, Postgres database, and data pipeline.

## Dependencies

- `python-3.10`
- `poetry`
- `docker`

## Instructions

### Docker

#### Secrets
Docker will expect to find secrets in `docker/secrets/`.

Password for each of the following Postgres users:

- `bga_pipeline_password.txt`
- `bga_user_password.txt`
- `postgres_password.txt`

BGG login credentials:

- `bgg_username.txt`
- `bgg_password.txt`

Once the secrets and `.env` file are ready, the stack is ready to be spun up.

#### Running

Make commands have been created for most interactions:

```bash
make run-pipeline-job # Run only the pipeline container. Requires rest of stack to be up already

make run-web-stack  # Run the stack without starting a data pipeline job

make run-full-stack  # Run the full Docker compose stack

make stop-stack  # Stop the Docker compose stack

make stack-logs  # Follow the Docker compose logs
```

Alternatively, you can use `docker compose -f docker/compose.yaml` to directly interact with the docker stack. 


### Development

To run locally, install the virtual environment using `poetry install`.
