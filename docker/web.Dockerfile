FROM python:3.10-alpine

WORKDIR /app

COPY ../poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --with web

COPY ../app ./app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]