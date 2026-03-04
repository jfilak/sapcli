"""ABAP Unit Test Framework ADT fixtures"""

AUNIT_NO_TEST_RESULTS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <alerts>
    <alert kind="noTestClasses" severity="tolerable">
      <title>The task definition does not refer to any test</title>
    </alert>
  </alerts>
</aunit:runResult>
'''

AUNIT_RESULTS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/runtime/traces/coverage/measurements/FOOBAR"/>
  </external>
  <program adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore" adtcore:type="CLAS/OC" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" uriType="semantic" xmlns:adtcore="http://www.sap.com/adt/core">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" adtcore:type="CLAS/OL" adtcore:name="LTCL_TEST" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_FAIL" executionTime="0.033" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" unit="s">
            <alerts>
              <alert kind="failedAssertion" severity="critical">
                <title>Critical Assertion Error: 'I am supposed to fail'</title>
                <details>
                  <detail text="True expected"/>
                  <detail text="Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'."/>
                </details>
                <stack>
                  <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#start=19,0" adtcore:type="CLAS/OCN/testclasses" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" adtcore:description="Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)"/>
                </stack>
              </alert>
            </alerts>
          </testMethod>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_WARN" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_WARN" executionTime="0.033" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_WARN" unit="s">
            <alerts>
              <alert kind="failedAssertion" severity="tolerable">
                <title>Warning: 'I am supposed to warn'</title>
                <details>
                  <detail text="True expected"/>
                  <detail text="Test 'LTCL_TEST-&gt;DO_THE_WARN' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'."/>
                </details>
                <stack>
                  <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#start=19,0" adtcore:type="CLAS/OCN/testclasses" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" adtcore:description="Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_WARN)"/>
                </stack>
              </alert>
            </alerts>
          </testMethod>
        <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_TEST" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST_HARDER" adtcore:type="CLAS/OL" adtcore:name="LTCL_TEST_HARDER" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST_HARDER" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST_HARDER%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_FAIL" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST_HARDER%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" unit="s">
            <alerts>
              <alert kind="failedAssertion" severity="critical">
                <title>Critical Assertion Error: 'I am supposed to fail'</title>
                <details>
                  <detail text="True expected"/>
                  <detail text="Test 'LTCL_TEST_HARDER-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'."/>
                </details>
                <stack>
                  <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#start=19,0" adtcore:type="CLAS/OCN/testclasses" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" adtcore:description="Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)"/>
                </stack>
              </alert>
            </alerts>
          </testMethod>
        <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST_HARDER%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_TEST" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST_HARDER%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
  <program adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests" adtcore:type="PROG/P" adtcore:name="ZEXAMPLE_TESTS" uriType="semantic" xmlns:adtcore="http://www.sap.com/adt/core">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPL;name=LTCL_TEST" adtcore:type="PROG/PP" adtcore:name="LTCL_TEST" uriType="semantic" navigationUri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPL;name=LTCL_TEST" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPLM;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" adtcore:type="PROG/OLI" adtcore:name="DO_THE_FAIL" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPLM;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" unit="s">
            <alerts>
              <alert kind="failedAssertion" severity="critical">
                <title>Critical Assertion Error: 'I am supposed to fail'</title>
                <details>
                  <detail text="True expected"/>
                  <detail text="Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZEXAMPLE_TESTS'."/>
                </details>
                <stack>
                  <stackEntry adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests/source/main#start=24,0" adtcore:type="PROG/P" adtcore:name="ZEXAMPLE_TESTS" adtcore:description="Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;24&gt; (DO_THE_FAIL)"/>
                  <stackEntry adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests/source/main#start=24,0" adtcore:type="PROG/P" adtcore:name="ZEXAMPLE_TESTS" adtcore:description="Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;25&gt; (PREPARE_THE_FAIL)"/>
                </stack>
              </alert>
              <alert kind="failedAssertion" severity="critical">
                <title>Error&lt;LOAD_PROGRAM_CLASS_MISMATCH&gt;</title>
              </alert>
            </alerts>
          </testMethod>
          <testMethod adtcore:uri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPLM;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" adtcore:type="PROG/OLI" adtcore:name="DO_THE_TEST" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/programs/programs/zexample_tests/source/main#type=PROG%2FPLM;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
</aunit:runResult>
'''

AUNIT_RESULTS_NO_TEST_METHODS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/runtime/traces/coverage/measurements/FOOBAR"/>
  </external>
  <program adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore" adtcore:type="CLAS/OC" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" uriType="semantic" xmlns:adtcore="http://www.sap.com/adt/core">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" adtcore:type="CLAS/OL" adtcore:name="LTCL_TEST" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" durationCategory="short" riskLevel="harmless">
        <testMethods>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
</aunit:runResult>
'''

GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <program xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" uriType="semantic" durationCategory="short" riskLevel="harmless">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" adtcore:parentUri="/sap/bc/adt/oo/classes/zcl_test_class" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" durationCategory="short" riskLevel="harmless">
        <alerts>
          <alert kind="warning" severity="tolerable">
            <title>The global test class [ZCL_TEST_CLASS] is not abstract</title>
            <details>
              <detail text="You can find further informations in document &lt;CHAP&gt; &lt;SAUNIT_TEST_CL_POOL&gt;"/>
            </details>
          </alert>
        </alerts>
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main#type=CLAS%2FOM;name=DO_THE_TEST" adtcore:type="CLAS/OM/private" adtcore:name="DO_THE_TEST" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class/source/main#type=CLAS%2FOM;name=DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
</aunit:runResult>
'''

TEST_CLASS_WITH_SYS_ERROR_FOLLOWED_BY_GREEN_TEST_CLASS_AUNIT_RESULTS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <program xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class_green" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS_GREEN" uriType="semantic" durationCategory="short" riskLevel="harmless">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class_green/source/main" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS_GREEN" adtcore:parentUri="/sap/bc/adt/oo/classes/zcl_test_class_green" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class_green/source/main" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class_green/source/main#type=CLAS%2FOM;name=DO_THE_TEST" adtcore:type="CLAS/OM/private" adtcore:name="DO_THE_TEST" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class_green/source/main#type=CLAS%2FOM;name=DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>    
    </testClasses>
  </program>
  <program xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" uriType="semantic" durationCategory="short" riskLevel="harmless">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" adtcore:parentUri="/sap/bc/adt/oo/classes/zcl_test_class" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" durationCategory="short" riskLevel="harmless">
        <alerts>
          <alert kind="failedAssertion" severity="critical">
            <title>The global test class [ZCL_TEST_CLASS] is not abstract</title>
            <details>
              <detail text="Some detail text"/>
            </details>
            <stack>
                <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main#start=1,10" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" adtcore:description="Include: &lt;ZCL_TEST_CLASS=======CM010&gt; Line: &lt;1&gt;"/>
            </stack>            
          </alert>
        </alerts>
      </testClass>
    </testClasses>
  </program>  
</aunit:runResult>
'''

AUNIT_NO_EXECUTION_TIME_RESULTS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <program xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" uriType="semantic" durationCategory="short" riskLevel="harmless">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" adtcore:type="CLAS/OC" adtcore:name="ZCL_TEST_CLASS" adtcore:parentUri="/sap/bc/adt/oo/classes/zcl_test_class" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class/source/main" durationCategory="short" riskLevel="harmless">
        <alerts>
          <alert kind="warning" severity="tolerable">
            <title>The global test class [ZCL_TEST_CLASS] is not abstract</title>
            <details>
              <detail text="You can find further informations in document &lt;CHAP&gt; &lt;SAUNIT_TEST_CL_POOL&gt;"/>
            </details>
          </alert>
        </alerts>
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_test_class/source/main#type=CLAS%2FOM;name=DO_THE_TEST" adtcore:type="CLAS/OM/private" adtcore:name="DO_THE_TEST" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_test_class/source/main#type=CLAS%2FOM;name=DO_THE_TEST" unit="s"/>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
</aunit:runResult>
'''

AUNIT_SYNTAX_ERROR_XML = '''<?xml version="1.0" encoding="utf-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <program xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_foo" adtcore:type="CLAS/OC" adtcore:name="CL_FOO" uriType="semantic">
    <alerts>
      <alert aunit:hasSyntaxErrors="true" kind="warning" severity="critical">
        <title>CL_FOO has syntax errors and cannot be analyzed for existence of unit tests</title>
        <details>
          <detail text="&quot;ME-&gt;MEMBER&quot; is not type-compatible with formal parameter &quot;BAR&quot;."/>
        </details>
        <stack>
          <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/cl_foo/includes/testclasses#start=428" adtcore:description="CL_FOO======CCAU:428"/>
        </stack>
      </alert>
    </alerts>
  </program>
</aunit:runResult>
'''


AUNIT_API_RUN_STATUS_RUNNING_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" xmlns:atom="http://www.w3.org/2005/Atom">
<aunit:progress status="RUNNING" percentage="50"/>
</aunit:run>'''

AUNIT_API_RUN_STATUS_FINISHED_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" xmlns:atom="http://www.w3.org/2005/Atom">
<aunit:progress status="FINISHED" percentage="100"/>
<atom:link href="/sap/bc/adt/abapunit/results/RUN_ID_123" rel="results" type="application/xml"/>
</aunit:run>'''

AUNIT_API_RUN_STATUS_FINISHED_REAL_XML = '''<?xml version="1.0" encoding="utf-8"?>\
<aunit:run title="Run" context="ABAP Unit Test Run" xmlns:aunit="http://www.sap.com/adt/api/aunit">\
<aunit:progress status="FINISHED" percentage="100"/>\
<aunit:executedBy user="DEVELOPER"/>\
<aunit:time started="2026-03-02T05:34:43Z" ended="2026-03-02T05:35:42Z"/>\
<atom:link href="/sap/bc/adt/abapunit/results/6D664D9B46CB1FE185BF306327ADDA18" \
rel="http://www.sap.com/adt/relations/api/abapunit/run-result" \
type="application/vnd.sap.adt.api.junit.run-result.v1+xml" \
title="Run Result (JUnit Format)" xmlns:atom="http://www.w3.org/2005/Atom"/>\
<atom:link href="/sap/bc/adt/abapunit/results/6D664D9B46CB1FE185BF306327ADDA18" \
rel="http://www.sap.com/adt/relations/api/abapunit/run-result" \
type="application/vnd.sap.adt.api.abapunit.run-result.v1+xml" \
title="Run Result (ABAP Unit Format)" xmlns:atom="http://www.w3.org/2005/Atom"/>\
</aunit:run>'''

AUNIT_API_JUNIT_RESULTS_XML = '''<?xml version="1.0" encoding="utf-8"?>\
<testsuites title="Run" system="C50" client="100" executedBy="DEVELOPER" \
time="59.227" timestamp="2026-03-02T05:34:43Z" \
failures="0" errors="0" skipped="0" asserts="0" tests="3">\
<testsuite name="" tests="1" failures="0" errors="0" skipped="0" asserts="0" \
package="odata_correspondence_v2" timestamp="2026-03-02T05:34:43Z" \
time="0.007" hostname="jakub-test--ddci-generic">\
<testcase classname="odata_correspondence_v2.clas:acl_fi_corr_req_entityset_dec---ltc_fi_corr_req_entityset_dec" \
name="test_decorations" time="0.005" asserts="0"/>\
</testsuite>\
<testsuite name="" tests="2" failures="0" errors="0" skipped="0" asserts="0" \
package="odata_correspondence_v2" timestamp="2026-03-02T05:34:43Z" \
time="0.013" hostname="jakub-test--ddci-generic">\
<testcase classname="odata_correspondence_v2.clas:cla_fi_corr_prm_rdr_db_bldr---ltcl_param_reader_db_conf" \
name="test_constructor" time="0.004" asserts="0"/>\
<testcase classname="odata_correspondence_v2.clas:cla_fi_corr_prm_rdr_db_bldr---ltcl_param_reader_db_conf" \
name="test_load_parameters" time="0.005" asserts="0"/>\
</testsuite>\
</testsuites>'''

AUNIT_RESULTS_SKIPPED_XML = '''<?xml version="1.0" encoding="utf-8"?>
<aunit:runResult xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/runtime/traces/coverage/measurements/FOOBAR"/>
  </external>
  <program adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore" adtcore:type="CLAS/OC" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" uriType="semantic" xmlns:adtcore="http://www.sap.com/adt/core">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" adtcore:type="CLAS/OL" adtcore:name="LTCL_TEST" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_FAIL" executionTime="0.033" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" unit="s">
            <alerts>
              <alert kind="abortion" severity="tolerable">
                <title>Missing Prerequisites - This test should not be executed here.</title>
                <details>
                  <detail text="Test execution skipped due to missing prerequisites"/>
                  <detail text="Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'."/>
                </details>
                <stack>
                  <stackEntry adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#start=19,0" adtcore:type="CLAS/OCN/testclasses" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" adtcore:description="Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)"/>
                </stack>
              </alert>
            </alerts>
          </testMethod>
        </testMethods>
      </testClass>
    </testClasses>
  </program>
</aunit:runResult>
'''
