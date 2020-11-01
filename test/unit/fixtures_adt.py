import sap.adt
from sap.adt.objects import xmlns_adtcore_ancestor
from sap.adt.annotations import xml_element, XmlElementKind

from mock import Response

OBJECT_METADATA = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')

EMPTY_RESPONSE_OK = Response(text='', status_code=200, headers={})

LOCK_RESPONSE_OK = Response(text='<sap><LOCK_HANDLE>win</LOCK_HANDLE></sap>',
                            status_code=200,
                            headers={'Content-Type': 'dataname=com.sap.adt.lock.Result'})

DEFINITIONS_READ_RESPONSE_OK = Response(text='* definitions',
                                         status_code=200,
                                         headers={'Content-Type': 'text/plain; charset=utf-8'})

IMPLEMENTATIONS_READ_RESPONSE_OK = Response(text='* implementations',
                                         status_code=200,
                                         headers={'Content-Type': 'text/plain; charset=utf-8'})

TEST_CLASSES_READ_RESPONSE_OK = Response(text='* test classes',
                                         status_code=200,
                                         headers={'Content-Type': 'text/plain; charset=utf-8'})

TASK_NUMBER='1A2B3C4D5E'
TRANSPORT_NUMBER='E5D4C3B2A1'

TASK_RELEASE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{TASK_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}" chkrun:status="released" chkrun:statusText="Transport request/task {TASK_NUMBER} was successfully released"/>
  </tm:releasereports>
</tm:root>'''

TASK_RELEASE_ERR_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{TASK_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}" chkrun:status="error" chkrun:statusText="Error"/>
  </tm:releasereports>
</tm:root>'''

TRASNPORT_RELEASE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newreleasejobs" tm:releasetimestamp="20190212191502 " tm:number="{TRANSPORT_NUMBER}">
  <tm:releasereports>
    <chkrun:checkReport xmlns:chkrun="http://www.sap.com/adt/checkrun" chkrun:reporter="transportrelease" chkrun:triggeringUri="/sap/bc/adt/cts/transportrequests/{TRANSPORT_NUMBER}" chkrun:status="released" chkrun:statusText="Transport request/task {TRANSPORT_NUMBER} was successfully released"/>
  </tm:releasereports>
</tm:root>'''

TRANSPORT_CREATE_OK_RESPONSE = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newrequest">
  <tm:request tm:number="{TRANSPORT_NUMBER}" tm:parent="" tm:desc="Transport Description" tm:type="K" tm:target="LOCAL" tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TRANSPORT_NUMBER}">
  </tm:request>
</tm:root>
'''

TASK_CREATE_OK_RESPONSE= f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:targetuser="FILAK" tm:useraction="tasks" tm:number="{TASK_NUMBER}" tm:uri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}">
</tm:root>
'''

SHORTENED_WORKBENCH_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" xmlns:adtcore="http://www.sap.com/adt/core">
    <tm:workbench tm:category="Workbench">
        <tm:target tm:name="/TGT/" tm:desc="Target Description">
            <tm:modifiable tm:status="Modifiable">
                <tm:request tm:number="{TRANSPORT_NUMBER}" tm:parent="" tm:owner="FILAK" tm:desc="Transport Description" tm:type="K" tm:status="D" tm:target="" tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:lastchanged_timestamp="20190206110506" tm:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TRANSPORT_NUMBER}">
                    <tm:long_desc/>
                    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/cts/transportrequests/{TRANSPORT_NUMBER}" rel="http://www.sap.com/cts/relations/adturi" type="application/vnd.sap.adt.transportrequests.v1+xml" title="Transport Organizer ADT URI"/>
                    <tm:abap_object tm:pgmid="CORR" tm:type="RELE" tm:name="NPLK000006 20190216 142210 DEVELOPER" tm:obj_info="Comment Entry: Released"/>
                    <tm:task tm:number="{TASK_NUMBER}" tm:parent="{TRANSPORT_NUMBER}" tm:owner="FILAK" tm:desc="Task Description" tm:type="Development/Correction" tm:status="D" tm:target="" tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:lastchanged_timestamp="20190212190504" tm:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/{TASK_NUMBER}">
                        <tm:long_desc/>
                        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}" rel="http://www.sap.com/cts/relations/adturi" type="application/vnd.sap.adt.transportrequests.v1+xml" title="Transport Organizer ADT URI"/>
                        <tm:abap_object tm:pgmid="LIMU" tm:type="TABD" tm:name="FOO" tm:wbtype="TABL/DS" tm:dummy_uri="/sap/bc/adt/cts/transportrequests/reference?obj_name=FOO&amp;obj_wbtype=TABD&amp;pgmid=LIMU" tm:obj_info="Table Definition" tm:obj_desc="Object Description" tm:position="000001" tm:lock_status="X" tm:img_activity="">
                                <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}" rel="http://www.sap.com/cts/relations/removeobject" type="application/xml" title="Transport Organizer Remove Locked Object"/>
                        </tm:abap_object>
                    </tm:task>
                </tm:request>
            </tm:modifiable>
        </tm:target>
    </tm:workbench>
</tm:root>
'''

SHORTENED_TRANSPORT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:object_type="R" adtcore:name="{TRANSPORT_NUMBER}" adtcore:type="RQRQ" adtcore:changedAt="2020-08-10T12:52:35Z" adtcore:changedBy="FILAK" adtcore:createdBy="FILAK" xmlns:adtcore="http://www.sap.com/adt/core">
    <tm:request tm:number="{TRANSPORT_NUMBER}" tm:parent="" tm:owner="FILAK" tm:desc="Transport Description" tm:type="K" tm:status="D" tm:status_text="Modifiable" tm:target="CTS_TARGET" tm:target_desc="Target Description" tm:cts_project="" tm:cts_project_desc="" tm:source_client="123" tm:lastchanged_timestamp="20200810125235" tm:uri="/sap/bc/adt/cts/transportrequests/{TRANSPORT_NUMBER}">
        <tm:attributes tm:attribute="SAPCORR" tm:description="Request created with correction request" tm:value="002075125900003621952020" tm:position="000001"/>
        <tm:task tm:number="{TASK_NUMBER}" tm:parent="{TRANSPORT_NUMBER}" tm:owner="FILAK" tm:desc="Task Description" tm:type="Unclassified" tm:status="D" tm:status_text="Modifiable" tm:target="" tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:source_client="123" tm:lastchanged_timestamp="20200810125235" tm:uri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}">
        </tm:task>
    </tm:request>
</tm:root>
'''

SHORTENED_TASK_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:object_type="T" adtcore:name="{TASK_NUMBER}" adtcore:type="RQRQ" adtcore:changedAt="2020-08-10T12:52:35Z" adtcore:changedBy="FILAK" adtcore:createdBy="FILAK" xmlns:adtcore="http://www.sap.com/adt/core">
    <tm:request tm:number="{TRANSPORT_NUMBER}" tm:parent="" tm:owner="FILAK" tm:desc="Transport Description" tm:type="K" tm:status="D" tm:status_text="Modifiable" tm:target="CTS_TARGET" tm:target_desc="Target Description" tm:cts_project="" tm:cts_project_desc="" tm:source_client="123" tm:lastchanged_timestamp="20200810125235" tm:uri="/sap/bc/adt/cts/transportrequests/{TRANSPORT_NUMBER}">
    </tm:request>
    <tm:task tm:number="{TASK_NUMBER}" tm:parent="{TRANSPORT_NUMBER}" tm:owner="FILAK" tm:desc="Task Description" tm:type="Unclassified" tm:status="D" tm:status_text="Modifiable" tm:target=""    tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:source_client="123" tm:lastchanged_timestamp="20200810125235" tm:uri="/sap/bc/adt/cts/transportrequests/{TASK_NUMBER}">
    </tm:task>
</tm:root>
'''

GET_DUMMY_OBJECT_ADT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<win:dummies xmlns:class="http://www.sap.com/adt/awesome/success" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:name="SOFTWARE_ENGINEER" adtcore:type="DUMMY/S" adtcore:changedAt="2019-03-07T20:22:01Z" adtcore:version="active" adtcore:createdAt="2019-02-02T00:00:00Z" adtcore:changedBy="DEVELOPER" adtcore:createdBy="DEVELOPER" adtcore:description="You cannot stop me!" adtcore:descriptionTextLimit="60" adtcore:language="CZ">
  <adtcore:packageRef adtcore:name='UNIVERSE'/>
</win:dummies>
'''

ERROR_XML_PACKAGE_ALREADY_EXISTS='''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="com.sap.adt"/><type id="ExceptionResourceAlreadyExists"/><message lang="EN">Resource Package $SAPCLI_TEST_ROOT does already exist.</message><localizedMessage lang="EN">Resource Package $SAPCLI_TEST_ROOT does already exist.</localizedMessage><properties/></exc:exception>'''

ERROR_XML_MADEUP_PROBLEM='''<?xml version="1.0" encoding="utf-8"?><exc:exception xmlns:exc="http://www.sap.com/abapxml/types/communicationframework"><namespace id="org.example.whatever"/><type id="UnitTestSAPCLI"/><message lang="EN">Made up problem.</message><localizedMessage lang="EN">Made up problem.</localizedMessage><properties/></exc:exception>'''

DISCOVERY_ADT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<app:service xmlns:app="http://www.w3.org/2007/app" xmlns:atom="http://www.w3.org/2005/Atom">
  <app:workspace>
    <atom:title>BOPF</atom:title>
    <app:collection href="/sap/bc/adt/bopf/businessobjects">
      <atom:title>Business Objects</atom:title>
      <app:accept>application/vnd.sap.ap.adt.bopf.businessobjects.v4+xml</app:accept>
      <app:accept>application/vnd.sap.ap.adt.bopf.businessobjects.v2+xml</app:accept>
      <app:accept>application/vnd.sap.ap.adt.bopf.businessobjects.v3+xml</app:accept>
      <atom:category term="BusinessObjects" scheme="http://www.sap.com/adt/categories/businessobjects"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/businessobjects/newAttributeBinding" template="/sap/bc/adt/bopf/newAttributeBinding"/>
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/businessobjects/actionExportingParameter" template="/sap/bc/adt/bopf/actionExportingParameter"/>
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/businessobjects/draftObject" template="/sap/bc/adt/bopf/draftObject"/>
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/businessobjects/nodeProperty" template="/sap/bc/adt/bopf/nodeProperty"/>
      </adtcomp:templateLinks>
    </app:collection>
    <app:collection href="/sap/bc/adt/bopf/businessobjects/$validation">
      <atom:title>Validation</atom:title>
      <atom:category term="Validation" scheme="http://www.sap.com/adt/categories/businessobjects"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/businessobjects/validation" template="/sap/bc/adt/bopf/businessobjects/$validation{?context,objname,baseobjname,nodename,persistent,transient,entitytype,classname,datatype,paramtype,resulttype,queryName}"/>
      </adtcomp:templateLinks>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>Packages</atom:title>
    <app:collection href="/sap/bc/adt/packages">
      <atom:title>Packages</atom:title>
      <app:accept>application/vnd.sap.adt.packages.v1+xml</app:accept>
      <atom:category term="devck" scheme="http://www.sap.com/wbobj/packages"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
        <adtcomp:templateLink rel="applicationcomponents" template="/sap/bc/adt/packages/valuehelps/applicationcomponents"/>
        <adtcomp:templateLink rel="softwarecomponents" template="/sap/bc/adt/packages/valuehelps/softwarecomponents"/>
        <adtcomp:templateLink rel="transportlayers" template="/sap/bc/adt/packages/valuehelps/transportlayers"/>
        <adtcomp:templateLink rel="translationrelevances" template="/sap/bc/adt/packages/valuehelps/translationrelevances"/>
      </adtcomp:templateLinks>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>Function Groups; Functions; Function Group Includes</atom:title>
    <app:collection href="/sap/bc/adt/functions/validation">
      <atom:title>Function Group Validation</atom:title>
      <atom:category term="validation" scheme="http://www.sap.com/adt/categories/functions"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility"/>
    </app:collection>
    <app:collection href="/sap/bc/adt/functions/groups">
      <atom:title>Function Groups</atom:title>
      <app:accept>application/vnd.sap.adt.functions.groups.v2+xml</app:accept>
      <atom:category term="groups" scheme="http://www.sap.com/adt/categories/functions"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
        <adtcomp:templateLink title="Function Modules" rel="http://www.sap.com/adt/categories/functiongroups/functionmodules" template="/sap/bc/adt/functions/groups/{groupname}/fmodules" type="application/vnd.sap.adt.functions.fmodules.v3+xml"/>
        <adtcomp:templateLink title="Function Group Includes" rel="http://www.sap.com/adt/categories/functiongroups/includes" template="/sap/bc/adt/functions/groups/{groupname}/includes" type="application/vnd.sap.adt.functions.fincludes.v2+xml"/>
      </adtcomp:templateLinks>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>ABAP DDL Sources</atom:title>
    <app:collection href="/sap/bc/adt/ddic/ddl/formatter/identifiers">
      <atom:title>DDL Case Preserving Formatter for Identifiers</atom:title>
      <app:accept>text/plain</app:accept>
      <atom:category term="formatter/identifiers" scheme="http://www.sap.com/adt/categories/ddic/ddlsources"/>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>Annotation Pushdown: Get Meta Data Extentions</atom:title>
    <app:collection href="/sap/bc/adt/sadl/gw/mde">
      <atom:title>SADL: Annotation Pushdown Metadata Extentions</atom:title>
      <app:accept>application/xml</app:accept>
      <atom:category term="SADLAnnotationPushdownMetaDataExtensions" scheme="http://www.sap.com/adt/categories/sadl/gw/mde"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility"/>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>Quickfixes</atom:title>
    <app:collection href="/sap/bc/adt/quickfixes/evaluation">
      <atom:title>Quickfixes</atom:title>
      <app:accept>application/vnd.sap.adt.quickfixes.evaluation+xml;version=1.0.0</app:accept>
      <atom:category term="evaluation" scheme="http://www.sap.com/adt/categories/quickfixes"/>
    </app:collection>
  </app:workspace>
  <app:workspace>
    <atom:title>Web Dynpro</atom:title>
    <app:collection href="/sap/bc/adt/wdy/views">
      <atom:title>Webdynpro View</atom:title>
      <app:accept>application/vnd.sap.adt.wdy.view+xml</app:accept>
      <app:accept>application/vnd.sap.adt.wdy.view.v1+xml</app:accept>
      <atom:category term="Views" scheme="http://www.sap.com/adt/categories/webdynpro"/>
      <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
        <adtcomp:templateLink rel="http://www.sap.com/adt/categories/webdynpro/view/validatecontextbinding" template="/sap/bc/adt/wdy/views/{comp_name}/{view_name}{?_action,elementDefName,elementLibName,property}"/>
      </adtcomp:templateLinks>
    </app:collection>
  </app:workspace>
</app:service>
'''

class DummyADTObject(sap.adt.ADTObject):

    OBJTYPE = sap.adt.ADTObjectType(
        'DUMMY/S',
        'awesome/success',
        xmlns_adtcore_ancestor('win', 'http://www.example.com/never/lose'),
        ['application/vnd.sap.super.cool.txt+xml', 'application/vnd.sap.super.cool.txt.v2+xml'],
        {'text/plain': 'no/bigdeal'},
        'dummies',
        editor_factory=sap.adt.objects.ADTObjectSourceEditor
    )

    def __init__(self, connection='noconnection', name='noobject', metadata=None):
        super(DummyADTObject, self).__init__(connection, name,
                                             metadata if metadata is not None else sap.adt.ADTCoreData(description='adt fixtures dummy object'))

    @xml_element('elemv2', kind=XmlElementKind.TEXT, version=['2'])
    def elemv2(self):
        return 'version2'
