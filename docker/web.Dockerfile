FROM python:3.10-alpine

WORKDIR /src

COPY ../poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main,web

COPY ../src/common ./common
COPY ../src/web ./web

CMD ["fastapi", "run", "web/main.py", "--port", "80"]