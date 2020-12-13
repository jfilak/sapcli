ACOVERAGE_RESULTS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<cov:result xmlns:cov="http://www.sap.com/adt/cov" name="ADT_ROOT_NODE">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR" rel="self"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/bulkstatements"/>
  <nodes>
    <node>
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/packages/test_check_list" adtcore:type="DEVC/K" adtcore:name="TEST_CHECK_LIST"/>
      <coverages>
        <coverage type="branch" total="134" executed="29"/>
        <coverage type="procedure" total="52" executed="10"/>
        <coverage type="statement" total="331" executed="96"/>
      </coverages>
      <nodes>
        <node>
          <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=49,6" adtcore:type="CLAS/OCI" adtcore:name="FOO===========================CP" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
          <coverages>
            <coverage type="branch" total="29" executed="22"/>
            <coverage type="procedure" total="8" executed="8"/>
            <coverage type="statement" total="63" executed="60"/>
          </coverages>
          <nodes>
            <node>
              <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=49,6" adtcore:type="CLAS/OCI" adtcore:name="FOO" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
              <coverages>
                <coverage type="branch" total="29" executed="22"/>
                <coverage type="procedure" total="8" executed="8"/>
                <coverage type="statement" total="63" executed="60"/>
              </coverages>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements/ADT_ROOT_NODE/TEST_CHECK_LIST/FOO%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3dCP/FOO" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/statements" type="application/xml+scov"/>
              <nodes>
                <node>
                  <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=52,9" adtcore:type="CLAS/OM" adtcore:name="METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
                  <coverages>
                    <coverage type="branch" total="5" executed="3"/>
                    <coverage type="procedure" total="1" executed="1"/>
                    <coverage type="statement" total="5" executed="5"/>
                  </coverages>
                </node>
                <node>
                  <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=199,1" adtcore:type="CLAS/OM" adtcore:name="METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
                  <coverages>
                    <coverage type="branch" total="2" executed="1"/>
                    <coverage type="procedure" total="1" executed="1"/>
                    <coverage type="statement" total="8" executed="6"/>
                  </coverages>
                </node>
              </nodes>
            </node>
          </nodes>
        </node>
        <node>
          <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/bar/source/main#start=13,6" adtcore:type="CLAS/OCI" adtcore:name="BAR===========================CP" adtcore:parentUri="/sap/bc/adt/oo/classes/bar"/>
          <coverages>
            <coverage type="branch" total="0" executed="0"/>
            <coverage type="procedure" total="0" executed="0"/>
            <coverage type="statement" total="0" executed="0"/>
          </coverages>
        </node>
      </nodes>
    </node>
  </nodes>
</cov:result>
'''


ACOVERAGE_STATEMENTS_RESULTS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
    <cov:statementsBulkResponse xmlns:cov="http://www.sap.com/adt/cov">
  <cov:statementsResponse name="FOO===========================CP.FOO.METHOD_A">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/A6B627DB009F1EEB8FAA3720D9128253/statements/ADT_ROOT_NODE/ODATA_MM_PUR_TEST_CHECK_LIST/FOO%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3dCP/FOO/METHOD_A" rel="self"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" xmlns:adtcore="http://www.sap.com/adt/core" href="/sap/bc/adt/oo/classes/foo/source/main#start=52,9" rel="http://www.sap.com/adt/relations/source" etag="20201209141757001000081" adtcore:changedAt="2020-12-09T14:17:57Z"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/A6B627DB009F1EEB8FAA3720D9128253/node/ADT_ROOT_NODE/ODATA_MM_PUR_TEST_CHECK_LIST/FOO%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3dCP/FOO/METHOD_A" rel="up" cov:outdated="false"/>
    <procedure executed="4">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=52,1;end=52,22" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </procedure>
    <statement executed="4">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=53,1;end=53,38" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      <branch kind="conditional" executedTrue="3" executedFalse="1">
        <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=53,1;end=53,38" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      </branch>
    </statement>
    <statement executed="3">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=54,1;end=54,64" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      <branch kind="conditional" executedTrue="&gt;= 3" executedFalse="0">
        <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=54,1;end=54,64" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      </branch>
    </statement>
    <statement executed="3">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=55,1;end=55,81" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="3">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=56,1;end=56,34" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="4">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=59,1;end=59,12" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_A" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
  </cov:statementsResponse>
  <cov:statementsResponse name="FOO================CP.FOO.METHOD_B">
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/A6B627DB009F1EEB8FAA3720D9128253/statements/ADT_ROOT_NODE/ODATA_MM_PUR_TEST_CHECK_LIST/FOO%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3dCP/FOO/METHOD_B" rel="self"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" xmlns:adtcore="http://www.sap.com/adt/core" href="/sap/bc/adt/oo/classes/foo/source/main#start=199,9" rel="http://www.sap.com/adt/relations/source" etag="20201209141757001000081" adtcore:changedAt="2020-12-09T14:17:57Z"/>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/A6B627DB009F1EEB8FAA3720D9128253/node/ADT_ROOT_NODE/ODATA_MM_PUR_TEST_CHECK_LIST/FOO%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3d%3dCP/FOO/METHOD_B" rel="up" cov:outdated="false"/>
    <procedure executed="5">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=199,1;end=199,29" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </procedure>
    <statement executed="5">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=209,1;end=209,50" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="5">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=212,1;end=212,30" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      <branch kind="conditional" executedTrue="2" executedFalse="3">
        <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=212,1;end=212,30" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      </branch>
    </statement>
    <statement executed="2">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=215,1;end=215,59" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="2">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=216,1;end=216,55" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="3">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=219,1;end=219,39" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      <branch kind="conditional" executedTrue="2" executedFalse="1">
        <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=219,1;end=219,39" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
      </branch>
    </statement>
    <statement executed="2">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=220,1;end=220,41" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="0">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=224,1;end=224,24" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
    <statement executed="0">
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=225,1;end=225,59" adtcore:type="CLAS/OM" adtcore:name="FOO                METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
    </statement>
  </cov:statementsResponse>
</cov:statementsBulkResponse>
'''