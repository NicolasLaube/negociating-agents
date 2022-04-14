install:
		pip install -r requirements.txt

install-dev: install
	pip install pre-commit==2.15.0
	pre-commit install
	pre-commit install --hook-type commit-msg
	pip install -r requirements-dev.txt

lint:
		python -m pylint communication tests
		python -m mypy communication tests
		python -m flake8 communication tests

cars:
	python -m communication --mode=cars --num_agents=2

presidential:
	python -m communication --mode=presidential --num_agents=10
