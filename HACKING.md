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

4. all development dependencies are tracked in the file [dev-requirements.txt](dev-requirements.txt) and can be installed with the following command

```bash
pip install -r dev-requirements.txt
```

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

You can also test subset (or single test case) by providing test case name
pattern:

```bash
python -m unittest discover -b -v -s test/unit -k test-name-pattern
```

Or if you see a test failure and you need to quickly run that one test case,
you can make use of the wrapper script `test/unit/runtest.sh`:

```bash
./test/unit/runtest.sh test_sap_cli_gcts.TestgCTSRepoMessages
```

Where `test_sap_cli_gcts` refers to `test/unit/test_sap_cli_gcts.py`
and TestgCTSRepoMessages is a test class.

4. Check code coverage - run either `make report-coverage` or

```bash
coverage run -m unittest discover -b -v -s test/unit
coverage report bin/sapcli $(find sap -type f -name '*.py')
```

You can also use `html` instead of `run` which will create
the report at the path `SOURCE_CODE_DIR/htmlcov/index.html`.
(Of course, the convenience make target exists - `report-coverage-html`).
