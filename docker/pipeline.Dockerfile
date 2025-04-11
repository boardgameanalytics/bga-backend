FROM python:3.10-alpine

WORKDIR /src

COPY ../poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main,pipeline

COPY ../services/common ./common
COPY ../services/pipeline ./pipeline

CMD ["python", "-m", "pipeline.run_job"]