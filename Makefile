# Purpose: Shell Script 
# (only damoster dev env has 2 different pythons...and python2 is no longer supported...)
PYTHON=python
PIP=pip

clean:
	find . -name '*.py?' -delete

# Running
init:
	$(PIP) install -Ur requirements.txt

run: clean
	$(PYTHON) main.py

# Development
freeze:
	$(PIP) freeze | grep -v "pkg-resources" > requirements.txt

test: clean
	pytest

lint:
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=env/*