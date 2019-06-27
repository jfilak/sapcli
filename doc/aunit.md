# ABAP Unit

## Usage

Execute `sapcli` with the parameters `aunit run {package|class|program} $OBJECT_NAME`.

The exit code will be determined based on test results where exit code is the
number of failed and erroed tests.

## Output format

### Raw

Tests results are printed in the form as they were returned from ADT.

### Human

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

### JUnit

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
