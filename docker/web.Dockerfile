FROM python:3.10-alpine

WORKDIR /src

COPY ../poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main,web

COPY ../services/common ./common
COPY ../services/web ./web

CMD ["fastapi", "run", "web/main.py", "--port", "80"]