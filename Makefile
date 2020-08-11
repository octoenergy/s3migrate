SHELL := /bin/bash

.PHONY: all reset update clean sync test lint unit integration

all: reset test

# Local installation

reset: clean update

update:
	pipenv update --dev

clean:
	rm -rf build dist htmlcov
	find src -type d -name __pycache__ | xargs rm -rf
	pipenv clean

sync:
	pipenv sync --dev

# Testing
lint:
	pipenv run flake8 src
	pipenv run mypy src
	# pipenv run pydocstyle src
	pipenv run flake8 tests
	pipenv run mypy tests

test:
	pipenv run pytest tests/

format:
	black -l 99 src
	black -l 99 tests
	isort src
	isort tests

# Deployment
package:
	pipenv run python setup.py bdist_wheel

circleci:
	circleci config validate

# Release
release:
	pipenv run python setup.py sdist 
	twine upload dist/*
