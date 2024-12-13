# Task: Set up the virtual environment and install dependencies
setup:
	poetry install

# Task: Format code using black
format:
	poetry run black .

# Task: Lint code using ruff
lint:
	poetry run ruff check --fix .

# Task: Run the application
run:
	poetry run python -m counter.entrypoints.webapp

# Task: Start PostgreSQL container
start-db:
	docker start test-postgres || docker run --name test-postgres -e POSTGRES_PASSWORD=postgres -d -p 5400:5432 postgres

# Task: Run tests using Pytest
test: start-db
	poetry run pytest

# Task: Clean up (remove virtual environment)
clean:
	poetry env remove python

