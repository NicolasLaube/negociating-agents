install:
		pip install -r requirements.txt
lint:
		python -m pylint communication tests
		python -m mypy communication tests
		python -m flake8 communication tests

test:
		pytest

tests: test

run:
	python -m communication
