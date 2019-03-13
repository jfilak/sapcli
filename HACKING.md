# Hacking

Start with extending API functionality and use it in your CLI commands - IOW do
not put too much logic into the CLI commands.

## Set up

1. you need pylint and flake8 which makes sure you follow coding style

2. you might consider installing GNU/make which is used to simplify developers
   workflow - there is [Makefile](Makefile) including the steps for checking
   code style and running tests

3. tests are written in python.unittest to avoid unnecessary dependencies and
   are stored in the directory [test/](test/)

## Workflow

1. Do your changes

2. Run linters - either `make lint` or

```bash
pylint --rcfile=.pylintrc sap
PYTHONPATH=$(pwd):$PYTHONPATH pylint --rcfile=.pylintrc bin/sapcli
flake8 --config=.flake8 sap
PYTHONPATH=$(pwd):$PYTHONPATH flake8 --config=.flake8 bin/sapcli
```

3. Run tests - either `make test` or

```bash
python -m unittest discover -b -v -s test/unit
```
