FROM python:3.10-alpine

WORKDIR /pipeline

COPY ../poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --with pipeline

COPY ../pipeline ./pipeline

CMD ["python", "run.py"]