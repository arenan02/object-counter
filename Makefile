# Variables
VENV=.venv
PYTHON=python3

# Task: Set up the virtual environment and install dependencies
setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -r requirements.txt

# Task: Format code using ruff
format:
	. $(VENV)/bin/activate && ruff format .

# Task: Lint code using ruff
lint:
	. $(VENV)/bin/activate && ruff check --fix .

# Task: Clean up (remove virtual environment)
clean:
	rm -rf $(VENV)