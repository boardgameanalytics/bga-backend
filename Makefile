init-backend:
	poetry install --with backend

init-pipeline:
	poetry install --with pipeline

init:
	poetry install --with backend,pipeline,dev

lint:
	black . --check
	isort . --profile=black --check
	flake8
	mypy .

format:
	black .
	isort . --profile=black