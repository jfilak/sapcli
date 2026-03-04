ACOVERAGE_MEASUREMENTS_XML='''<?xml version="1.0" encoding="UTF-8"?>
<cov:result xmlns:cov="http://www.sap.com/adt/cov" name="ADT_ROOT_NODE">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR" rel="self"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/bulkstatements"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/measurements/6D664D9B46CB1FE1859107ADE8729541/coveredobjects" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/measurements/coveredobjects"/>
  <nodes>
    <node>
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/packages/test_example_package" adtcore:type="DEVC/K" adtcore:name="TEST_EXAMPLE_PACKAGE"/>
      <coverages>
        <coverage type="branch" total="2757" executed="1742"/>
        <coverage type="procedure" total="810" executed="561"/>
        <coverage type="statement" total="7518" executed="5652"/>
      </coverages>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=test_example_package&amp;type=devc/k" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
      <nodes>
        <node>
          <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/source/main#start=25,6" adtcore:type="CLAS/OCP" adtcore:name="CL_EXAMPLE_CLASS" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class" adtcore:description="Class-Pool"/>
          <coverages>
            <coverage type="branch" total="43" executed="42"/>
            <coverage type="procedure" total="43" executed="42"/>
            <coverage type="statement" total="86" executed="84"/>
          </coverages>
          <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class&amp;type=clas/ocp" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
          <nodes>
            <node>
              <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/source/main#start=25,6" adtcore:type="CLAS/OCI" adtcore:name="CL_EXAMPLE_CLASS" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class" adtcore:description="Base class for decoratros of /IWBEP/IF_MGW_REQ_ENTITYSET"/>
              <coverages>
                <coverage type="branch" total="42" executed="41"/>
                <coverage type="procedure" total="42" executed="41"/>
                <coverage type="statement" total="84" executed="82"/>
              </coverages>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/children/ADT_ROOT_NODE%2fTEST_EXAMPLE_PACKAGE%2fCL_EXAMPLE_CLASS%253dCP%2fCL_EXAMPLE_CLASS%2f" rel="next" type="application/xml+scov"/>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements/ADT_ROOT_NODE/TEST_EXAMPLE_PACKAGE/CL_EXAMPLE_CLASS%3dCP/CL_EXAMPLE_CLASS" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/statements" type="application/xml+scov"/>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class&amp;type=clas/oc" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
            </node>
            <node>
              <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/includes/testclasses#start=14,6" adtcore:type="CLAS/OCL" adtcore:name="LCL_STUB_DECORATOR" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class"/>
              <coverages>
                <coverage type="branch" total="1" executed="1"/>
                <coverage type="procedure" total="1" executed="1"/>
                <coverage type="statement" total="2" executed="2"/>
              </coverages>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/children/ADT_ROOT_NODE%2fTEST_EXAMPLE_PACKAGE%2fCL_EXAMPLE_CLASS%253dCP%2fLCL_STUB_DECORATOR%2f" rel="next" type="application/xml+scov"/>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements/ADT_ROOT_NODE/TEST_EXAMPLE_PACKAGE/CL_EXAMPLE_CLASS%3dCP/LCL_STUB_DECORATOR" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/statements" type="application/xml+scov"/>
              <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class.lcl_stub_decorator&amp;type=clas/op" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
            </node>
          </nodes>
        </node>
      </nodes>
    </node>
  </nodes>
</cov:result>
'''

ACOVERAGE_NEXT_OBJECT_MEASUREMENTS_XML='''<?xml version="1.0" encoding="UTF-8"?>
<cov:result xmlns:cov="http://www.sap.com/adt/cov" name="ADT_ROOT_NODE">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/6D664D9B46CB1FD185D93DEFEAFF9CB4/children/ADT_ROOT_NODE%2fTEST_EXAMPLE_PACKAGE%2fCL_EXAMPLE_CLASS%253dCP%2fCL_EXAMPLE_CLASS" rel="self"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/6D664D9B46CB1FD185D93DEFEAFF9CB4/statements/ADT_ROOT_NODE/TEST_EXAMPLE_PACKAGE/CL_EXAMPLE_CLASS%3dCP/CL_EXAMPLE_CLASS" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/bulkstatements"/>
  <nodes>
    <node>
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/source/main#start=28,9;end=28,64" adtcore:type="CLAS/OM/public" adtcore:name="/IWBEP/IF_MGW_REQ_COMMON~GET_SUPPORTED_RUNTIME_FEATURES" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class" adtcore:description="Get the supported runtime features"/>
      <coverages>
        <coverage type="statement" total="2" executed="2"/>
        <coverage type="procedure" total="1" executed="1"/>
        <coverage type="branch" total="1" executed="1"/>
      </coverages>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class./iwbep/if_mgw_req_common~get_supported_runtime_features&amp;type=clas/om/public" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
    </node>
    <node>
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/source/main#start=33,9;end=33,43" adtcore:type="CLAS/OM/public" adtcore:name="/IWBEP/IF_MGW_REQ_ENTITYSET~GET_AT" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class" adtcore:description="AT custom query option (at)"/>
      <coverages>
        <coverage type="statement" total="2" executed="2"/>
        <coverage type="procedure" total="1" executed="1"/>
        <coverage type="branch" total="1" executed="1"/>
      </coverages>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class./iwbep/if_mgw_req_entityset~get_at&amp;type=clas/om/public" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
    </node>
  </nodes>
</cov:result>
'''

ACOVERAGE_NEXT_2_OBJECT_MEASUREMENTS_XML='''<?xml version="1.0" encoding="UTF-8"?>
<cov:result xmlns:cov="http://www.sap.com/adt/cov" name="ADT_ROOT_NODE">
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/6D664D9B46CB1FE185E9AD68340349B2/children/ADT_ROOT_NODE%2fTEST_EXAMPLE_PACKAGE%2fCL_EXAMPLE_CLASS%253dCP%2fLCL_STUB_DECORATOR" rel="self"/>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/runtime/traces/coverage/results/6D664D9B46CB1FE185E9AD68340349B2/statements/ADT_ROOT_NODE/TEST_EXAMPLE_PACKAGE/CL_EXAMPLE_CLASS%3dCP/LCL_STUB_DECORATOR" rel="http://www.sap.com/adt/relations/runtime/traces/coverage/results/bulkstatements"/>
  <nodes>
    <node>
      <adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_example_class/includes/testclasses#start=16,9" adtcore:type="CLAS/OM/public/constructor" adtcore:name="CONSTRUCTOR" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_example_class/includes/testclasses#start=14,6"/>
      <coverages>
        <coverage type="statement" total="2" executed="2"/>
        <coverage type="procedure" total="1" executed="1"/>
        <coverage type="branch" total="1" executed="1"/>
      </coverages>
      <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/repository/informationsystem/elementinfo?path=cl_example_class.lcl_stub_decorator.constructor&amp;type=clas/oli" rel="http://www.sap.com/adt/relations/elementinfo" type="application/vnd.sap.adt.elementinfo+xml" title="Show Element Information"/>
    </node>
  </nodes>
</cov:result>
'''


