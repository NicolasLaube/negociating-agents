install:
		pip install -r requirements.txt
lint:
		python -m pylint communication tests
		python -m mypy communication tests
		python -m flake8 communication tests

test:
		pytest

tests: test

cars:
	python -m communication --mode=cars

presidential:
	python -m communication --mode=presidential
