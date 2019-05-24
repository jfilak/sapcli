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
  <program adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore" adtcore:type="CLAS/OC" adtcore:name="ZCL_THEKING_MANUAL_HARDCORE" uriType="semantic" xmlns:adtcore="http://www.sap.com/adt/core">
    <testClasses>
      <testClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" adtcore:type="CLAS/OL" adtcore:name="LTCL_TEST" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOCL;name=LTCL_TEST" durationCategory="short" riskLevel="harmless">
        <testMethods>
          <testMethod adtcore:uri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" adtcore:type="CLAS/OLI" adtcore:name="DO_THE_FAIL" executionTime="0" uriType="semantic" navigationUri="/sap/bc/adt/oo/classes/zcl_theking_manual_hardcore/includes/testclasses#type=CLAS%2FOLD;name=LTCL_TEST%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20DO_THE_FAIL" unit="s">
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
