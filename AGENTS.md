- this python projects has source codes located in the directory sap/
- use red/green test driven development - first tests, then production code
- tests are located in the directory test/unit/
- tests are written in python unittest
- tests expects PYTHONPATH pointing to the project root directory
- write tests sequentially without loops
- when witting code follow the rule Keep it simple stupid
- every module should have a special test file. Example: module sap/cli/gcts.py has tests in test/unit/test_sap_cli_gcts.py
- test fixtures are located in the same directory with test.
- test fixtures are stored as module files with the prefix fixtures_.
- the fixtures suffix should be matching the tested module the same way as test file.
- do use exception types derived from sap.errors.SAPCliError to make sure the
  command line entry point intercepts them and prints nice error message instead
  of stacktrace
- avoid silent swallowing caught exceptions - if you need it, add a comment explaining why it is needed
