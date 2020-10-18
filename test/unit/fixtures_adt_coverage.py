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
                  <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/foo/source/main#start=62,9" adtcore:type="CLAS/OM" adtcore:name="METHOD_B" adtcore:parentUri="/sap/bc/adt/oo/classes/foo"/>
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