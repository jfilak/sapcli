"""ABAP Unit Test Framework ADT fixtures for Command Line Interface"""

# https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd
# https://github.com/junit-team/junit5/blob/master/platform-tests/src/test/resources/jenkins-junit.xsd
# http://svn.apache.org/repos/asf/ant/core/trunk/src/main/org/apache/tools/ant/taskdefs/optional/junit/

AUNIT_NO_TEST_RESULTS_JUNIT = '''<?xml version="0.0" encoding="utf-8"?>
<testsuites name=(PACKAGE OR OBJECT passed by a user) tests= failures= disabled= errors= time=>
    <testsuite name= tests= failures= errors= disabled= skipped= timestamp= hostname= id= package= time=>
        <properties>
            <property name= value= >
        </properties>
        <testcase name= time= classname= status= >
            <error 
            <failure message= type= >
                alert
            </failure>
            <system-err>
                stack
            </system-err>
            <skipped/>
        </testcase>
    </testsuite>
</testsuites>

