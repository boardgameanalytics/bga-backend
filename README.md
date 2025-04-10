# BoardGameAnalytics Backend & Data Engineering Stack

## Overview

This repository hosts the backend and data engineering code for the BoardGameAnalytics stack. It uses Docker containers
to host the web backend, Postgres database, and data pipeline.

## Dependencies

- `python-3.10`
- `poetry`
- `docker`

## Instructions

Before running, a `.env` file needs to be created and stored in the root of the directory.

The following template should be used and completely filled out:

```
# Login credentials for boardgamegeek.com
BGG_USERNAME=
BGG_PASSWORD=

# Login credentials for the data pipeline to use
DB_USER=bga_pipeline
DB_PASSWORD=
DB_HOST=localhost
DB_NAME=boardgameanalytics_db

# Path to use within Docker instance to store intermediate data for pipeline
DATA_PATH=/data
```

### Docker

Docker will expect to find secrets in `docker/secrets/`.

Save the password for each Postgres user (bga_pipeline, bga_user, and postgres) to the like-named file:

- `bga_pipeline_password.txt`
- `bga_user_password.txt`
- `postgres_password.txt`

Once the secrets and `.env` file are ready, the stack is ready to be spun up.

Use `docker compose` to build and run the stack. One of the containers is the `pipeline_job`, which will populate the
database and then exit on completion.
```bash
docker compose up -d
```

You can follow the logs for the job as well:
```bash
docker compose logs pipeline_job
```

You can safely shut down the stack with:

```bash
docker compose down
```

If you want to start the stack without running the `pipeline_job`, you can do so using

```bash
docker compose up web db -d
```

### Development

To run locally, install the virtual environment using `poetry`. Dependencies are defined in optional groups for each
Docker image.

```bash
poetry install --with all
```
