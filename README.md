# BoardGameAnalytics Backend & Data Engineering Stack

## Overview

This repository hosts the backend and data engineering code for the BoardGameAnalytics backend stack. 
The stack is composed of three services: web-backend, db, and pipeline.

The web backend and database use FastAPI and Postgres, respectively. The pipeline container runs a script using the 
BGG_XML_API2 API provided by BoardGameGeeks.com to extract, transform, and load the top K ranked games on the site into
the Postgres database.

## Setup
Before running the application, you need to create a BGG user account and set up the necessary secrets.

1. **Create BoardGameGeek.com Account**
    - Create a free BGG user account and record the username and password for the next step. 
2. **Secrets:**
    - Copy the example secrets directory: `cp -r docker/secrets/example docker/secrets`
    - Populate the files in `docker/secrets/` with the appropriate values.  You'll need to set passwords for the 
      Postgres users (bga_pipeline, bga_user, postgres) and BoardGameGeek.com (BGG) login credentials.

Once these steps are complete, you can start the application using `make stack-up`.

**Note: When starting the full stack, the pipeline-job container will run and populate the database. It defaults to 
fetching data for the top 1000 board games on the BGG Rankings for the current day, but the number may be adjusted.

## Usage

### Makefile
Many common commands are pre-defined in a `Makefile` for ease of use, and may be quickly referenced using the 
`make help` command:

```
$ make help
---------------------------------------------------------------------------
bga-backend Makefile Commands
Stack refers to the Docker Compose stack defined in `docker/compose.yaml`.
---------------------------------------------------------------------------
lint                           Run linters and type checkers
format                         Run code formatters
test                           Run pytest suite
stack-build                    Build the stack
stack-up                       Run the full stack
stack-stop                     Stop the stack
stack-down                     Destroy the stack containers, keep persistent volumes
stack-logs                     Follow the stack logs
stack-logs-pipeline            Follow the logs for the pipeline container
stack-logs-web                 Follow the logs for the web container
stack-run-pipeline-only        Run only the pipeline container. Requires rest of stack to be up already
stack-run-web-only             Run the stack without starting a data pipeline job
```

### Web Backend

The web backend exposes a REST API using FastAPI.  Here are a few example endpoints:

*   `/games`: Retrieve a list of all games in the database.

**Example:**

```bash
curl http://localhost:80/games
```

### Pipeline
The pipeline can be run manually using the following command:

```
make stack-run-pipeline-only
```
This will execute the extract, transform, and load process, updating the database with the latest data.

## Docker

All Docker related files may be found within the `docker` directory.

### Secrets

Docker will expect to find secrets in `docker/secrets/`. Example files may be found in `docker/secrets/examples`

### Commands

To interact with the stack, use of the predefined Make commands is recommended:

```bash
stack-up                       # Run the full stack
stack-stop                     # Stop the stack
stack-down                     # Destroy the stack containers, keep persistent volumes
stack-logs                     # Follow the stack logs
```

For more granular control, commands are also available 
```bash
stack-logs-pipeline            # Follow the logs for the pipeline container
stack-logs-web                 # Follow the logs for the web container
stack-run-pipeline-only        # Run only the pipeline container. Requires rest of stack to be up already
stack-run-web-only             # Run the stack without starting a data pipeline job
```
