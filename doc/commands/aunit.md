# ABAP Unit

1. [run](#run)

## run

Execute `sapcli` with the parameters `aunit run {package|class|program|transport} OBJECT_NAME [OBJECT_NAME | ...]`.

The exit code will be determined based on test results where exit code is the
number of failed and erroed tests if _unit_ included in the result.

```bash
sapcli aunit run {package,class,program,program-include,transport} NAME [--output {raw,human,junit4}] [--as4user NAME] [--result {unit,coverage,all}] [--coverage-output {raw, human, jacoco}] [--coverage-filepath PATH]
```

- _transport_ : if you use transport, NAME is Transport Number
- _program-include_: sapcli will try to automatically determine the corresponding main program. If it cannot be done, it is possible to define the main program by prepending the main program's name to the parameter NAME the following way: "MAIN\_PROGRAM\_NAME\\NAME".
- _--as4user_ : used only for transports to be able to select the transport
- _--result_: desired result to be displayed
- _--coverage-filepath_: path where coverage output will be stored if one of _coverage_ or _all_ is selected as _result_

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

### Coverage output format

#### Raw

Coverage results are printed in the form as they were returned from ADT.

#### Human

This format attempts to provide nice human readable form of the coverage results.

```
PACKAGE FOO : 31.19%
  CLASS BAR : 95.52%
    METHOD A : 100.00%
    METHOD B : 75.00%
    METHOD C : 100.00%
```

#### JaCoCo

Coverage results are printed in the JaCoCo format as defined in:
- https://www.jacoco.org/jacoco/trunk/coverage/report.dtd
