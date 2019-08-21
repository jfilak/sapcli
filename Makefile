PYTHON_MODULE_DIR=./
PYTHON_MODULE=sap
PYTHON_BINARIES=bin/sapcli
PYTHON_MODULE_FILES=$(shell find $(PYTHON_MODULE) -type f -name '*.py')

TESTS_DIR=test
TESTS_UNIT_DIR=$(TESTS_DIR)/unit
TESTS_UNIT_FILES=$(shell find $(TESTS_UNIT_DIR) -type f -name '*.py')

PYTHON_BIN=python3

COVERAGE_BIN=coverage3
COVERAGE_CMD_RUN=$(COVERAGE_BIN) run
COVERAGE_CMD_REPORT=$(COVERAGE_BIN) report
COVERAGE_REPORT_ARGS=--skip-covered
COVERAGE_CMD_HTML=$(COVERAGE_BIN) html
COVERAGE_HTML_DIR=.htmlcov
COVERAGE_HTML_ARGS=$(COVERAGE_REPORT_ARGS) -d $(COVERAGE_HTML_DIR)
COVERAGE_REPORT_FILES=$(PYTHON_BINARIES) $(PYTHON_MODULE_FILES)

PYTEST_MODULE=unittest
PYTEST_PARAMS=discover -b -v -s $(TESTS_UNIT_DIR)

PYLINT_BIN ?= pylint-3
PYLINT_RC_FILE=.pylintrc
PYLINT_PARAMS=--output-format=parseable --reports=no

FLAKE8_BIN ?= flake8-3
FLAKE8_CONFIG_FILE=.flake8
FLAKE8_PARAMS=

.PHONY: lint
lint:
	$(PYLINT_BIN) --rcfile=$(PYLINT_RC_FILE) $(PYLINT_PARAMS) $(PYTHON_MODULE)
	PYTHONPATH=$(PYTHON_MODULE_DIR):$$PYTHONPATH $(PYLINT_BIN) --rcfile=$(PYLINT_RC_FILE) $(PYLINT_PARAMS) $(PYTHON_BINARIES)
	$(FLAKE8_BIN) --config=$(FLAKE8_CONFIG_FILE) $(FLAKE8_PARAMS) $(PYTHON_MODULE)
	PYTHONPATH=$(PYTHON_MODULE_DIR):$$PYTHONPATH $(FLAKE8_BIN) --config=$(FLAKE8_CONFIG_FILE) $(FLAKE8_PARAMS) $(PYTHON_BINARIES)

.PHONY: test
test:
	$(PYTHON_BIN) -m $(PYTEST_MODULE) $(PYTEST_PARAMS)

.coverage: $(COVERAGE_REPORT_FILES) $(TESTS_UNIT_FILES)
	$(MAKE) test PYTHON_BIN="$(COVERAGE_CMD_RUN)"

.PHONY: report-coverage
report-coverage: .coverage
	@ $(COVERAGE_CMD_REPORT) $(COVERAGE_REPORT_ARGS) $(COVERAGE_REPORT_FILES)

.PHONY: report-coverage-html
report-coverage-html: .coverage
	@ echo "Generating HTML code coverage report ..."
	@ $(COVERAGE_CMD_HTML) $(COVERAGE_HTML_ARGS) $(COVERAGE_REPORT_FILES)
	@ echo "Report: file://$$(pwd)/$(COVERAGE_HTML_DIR)/index.html"

.PHONY: system-test
system-test:
	export PATH=$$(pwd):$$PATH; cd test/system && ./run.sh

.PHONY: check
check: lint report-coverage

.PHONY: clean
clean:
	rm -rf .coverage $(COVERAGE_HTML_DIR)
