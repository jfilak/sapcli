# ABAP Unit

1. [run](#run)

## run

Execute `sapcli` with the parameters `aunit run {package|class|program|transport} $OBJECT_NAME`.

The exit code will be determined based on test results where exit code is the
number of failed and erroed tests.

```bash
sapcli aunit run {package,class,program,transport} NAME [--output {raw,human,junit4}] [--as4user NAME]
```

- _transport_ : if you use transport, NAME is Transport Number
- _--as4user_ : used only for transports to be able to select the transport

If you struggle to get Transport User, you can use [datapreview](datapreview.md):

```bash
sapcli datapreview osql --noheadings "SELECT as4user FROM e070 WHERE trkorr EQ '$CORRNR'"
```

### Output format

#### Raw

Tests results are printed in the form as they were returned from ADT.

#### Human

This format attempts to provide nice human readable form of the test results.

```
GLOBAL PUBLIC CLASS FOO
  LOCAL TEST CLASS A
    TEST METHOD1 [SUCCESS]
  LOCAL TEST CLASS B
    TEST METHOD1 [ERROR]
GLOBAL PUBLIC CLASS FOO
  LOCAL TEST CLASS A
    TEST METHOD1 [SKIPPED]
  LOCAL TEST CLASS B
    TEST METHOD1 [SUCCESS]

GLOBAL PUBLIC CLASS FOO=>LOCAL TEST CLASS A=>TEST METHOD1
* [critical] [failedAssertion] Assertion failed

Succeeded: 2
Skipped:   1
Failed:    1
```

#### JUnit

The JUnit format was assembled from:
- https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd
- https://github.com/junit-team/junit5/blob/master/platform-tests/src/test/resources/jenkins-junit.xsd
- http://svn.apache.org/repos/asf/ant/core/trunk/src/main/org/apache/tools/ant/taskdefs/optional/junit/

* testsuites
  - name: CLASS NAME | PROGRAM NAME | PACKAGE NAME

* testsuite
  - name: testClass[name]
  - package: CLASS NAME | PROGRAM NAME

* testcase
  - name: testMethod[name]
  - skipped: alert[kind]
  - system-err: alert/details

* error: alert
  - message: title
  - type: kind
  - text = alert/stack

#### Sonar

Test results are printed in the Sonar "Generic Execution" format as defined in:
- https://docs.sonarqube.org/latest/analysis/generic-test/

If the code was previously checked, an attempt is made to match up the test classes with their corresponding files:

```bash
sapcli checkout package {packagename}
sapcli aunit run package {packagename} --output sonar
```

If the command is run without checking out the code, or if no matching test class can be found, a synthentic path
is used with the format `PACKAGE-NAME/CLASS-NAME=>TEST-CLASS-NAME`.

Alerts generated for the test class are represented as a `testCase` with the `name` property set to the name of the
test class.
