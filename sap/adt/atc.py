"""ATC ADT wrappers"""

import xml.sax
from xml.sax.handler import ContentHandler

from typing import NamedTuple

from sap import get_logger
from sap.adt.objects import OrderedClassMembers, ADTObjectType, XMLNamespace, xmlns_adtcore_ancestor
from sap.adt.annotations import xml_element, XmlNodeProperty, xml_text_node_property, XmlContainer, \
    XmlNodeAttributeProperty
from sap.adt.marshalling import Marshal
from sap.adt.datapreview import DataPreview


CUSTOMIZING_MIME_TYPE_V1 = 'application/vnd.sap.atc.customizing-v1+xml'

XMLNS_ATC = XMLNamespace('atc', 'http://www.sap.com/adt/atc')
XMLNS_ATCINFO = XMLNamespace('atcinfo', 'http://www.sap.com/adt/atc/info')
XMLNS_ATCWORKLIST = XMLNamespace('atcworklist', 'http://www.sap.com/adt/atc/worklist')
XMLNS_ATCOBJECT = xmlns_adtcore_ancestor('atcobject', 'http://www.sap.com/adt/atc/object')
XMLNS_ATCFINDING = XMLNamespace('atcfinding', 'http://www.sap.com/adt/atc/finding')


def mod_log():
    """Returns logger for this module"""

    return get_logger()


class ATCCustomizingXMLHandler(ContentHandler):
    """ATC Customizing XML parser"""

    def __init__(self, customizing):
        """:param customizing: A object with the target attributes"""
        super().__init__()

        self.customizing = customizing

    def startElement(self, name, attrs):
        if name == 'property' and attrs.get('name', None) == 'systemCheckVariant':
            self.customizing.system_check_variant = attrs.get('value', None)


# pylint: disable=too-few-public-methods
class Customizing:
    """ATC Customizing"""

    def __init__(self, system_check_variant=None):
        self.system_check_variant = system_check_variant


def fetch_customizing(connection):
    """Fetch ATC customizing for the connected system"""

    resp = connection.execute(
        'GET',
        'atc/customizing',
        accept=['application/xml', CUSTOMIZING_MIME_TYPE_V1]
    )

    mod_log().debug('ATC Customizing response:\n%s', resp.text)

    cust = Customizing()
    xml.sax.parseString(resp.text, ATCCustomizingXMLHandler(cust))

    return cust


class RunRequest(metaclass=OrderedClassMembers):
    """Worklist run Request"""

    objtype = ADTObjectType(None, None, XMLNS_ATC, 'application/xml', None, 'run')

    max_verdicts = XmlNodeAttributeProperty('maximumVerdicts')

    def __init__(self, obj_sets, max_verdicts):
        """:param obj_sets: An instance of :class:`ADTObjectSets`
           :param max_verdicts: A number
        """
        self._sets = obj_sets
        self.max_verdicts = max_verdicts

    @xml_element('objectSets')
    def sets(self):
        """Set of objects which we want to check"""

        return self._sets


class ATCInfo(metaclass=OrderedClassMembers):
    """atcinfo:info XML Node"""

    objtype = ADTObjectType(None, None, XMLNS_ATCINFO, 'application/xml', None, 'info')

    typ = xml_text_node_property('atcinfo:type')
    description = xml_text_node_property('atcinfo:description')

    def __str__(self):
        return self.description


# pylint: disable=invalid-name
ATCInfoList = XmlContainer.define(ATCInfo.objtype.xmlelement, ATCInfo)


class RunResponse(metaclass=OrderedClassMembers):
    """Worklist run Response"""

    objtype = ADTObjectType(None, None, XMLNS_ATCWORKLIST, 'application/xml', None, 'worklistRun')

    worklist_id = xml_text_node_property('atcworklist:worklistId')
    timestamp = xml_text_node_property('atcworklist:worklistTimestamp')
    infos = XmlNodeProperty('atcworklist:infos', factory=ATCInfoList)


class WorkListObjectSet(metaclass=OrderedClassMembers):
    """atcworklist:objectSet XML Node"""

    name = XmlNodeAttributeProperty('atcworklist:name')
    title = XmlNodeAttributeProperty('atcworklist:title')
    kind = XmlNodeAttributeProperty('atcworklist:kind')


# pylint: disable=invalid-name
WorkListObjectSetList = XmlContainer.define('atcworklist:objectSet', WorkListObjectSet)


class ATCFinding(metaclass=OrderedClassMembers):
    """atcfinding:finding XML Node"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    location = XmlNodeAttributeProperty('atcfinding:location')
    priority = XmlNodeAttributeProperty('atcfinding:priority')
    check_id = XmlNodeAttributeProperty('atcfinding:checkId')
    check_title = XmlNodeAttributeProperty('atcfinding:checkTitle')
    message_id = XmlNodeAttributeProperty('atcfinding:messageId')
    message_title = XmlNodeAttributeProperty('atcfinding:messageTitle')
    exemption_approval = XmlNodeAttributeProperty('atcfinding:exemptionApproval')
    exemption_kind = XmlNodeAttributeProperty('atcfinding:exemptionKind')


# pylint: disable=invalid-name
ATCFindingList = XmlContainer.define('atcfinding:finding', ATCFinding)


class ATCObject(metaclass=OrderedClassMembers):
    """atcobject:object XML Node"""

    objtype = ADTObjectType(None, None, XMLNS_ATCOBJECT, 'application/xml', None, 'object')

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')
    package_name = XmlNodeAttributeProperty('adtcore:packageName')
    author = XmlNodeAttributeProperty('atcobject:author')
    object_type_id = XmlNodeAttributeProperty('atcobject:objectTypeId')
    findings = XmlNodeProperty('atcobject:findings', factory=ATCFindingList)


# pylint: disable=invalid-name
ATCObjectList = XmlContainer.define('atcobject:object', ATCObject)


class WorkList(metaclass=OrderedClassMembers):
    """atcworklist:worklist XML Node"""

    objtype = ADTObjectType(None, None, XMLNS_ATCWORKLIST, 'application/xml', None, 'worklist')

    worklist_id = XmlNodeAttributeProperty('atcworklist:id')
    timestamp = XmlNodeAttributeProperty('atcworklist:timestamp')
    used_objectset = XmlNodeAttributeProperty('atcworklist:usedObjectSet')
    object_set_is_complete = XmlNodeAttributeProperty('atcworklist:objectSetIsComplete')
    object_sets = XmlNodeProperty('atcworklist:objectSets', factory=WorkListObjectSetList)
    objects = XmlNodeProperty('atcworklist:objects', factory=ATCObjectList)


class WorkListRunResult(NamedTuple):
    """Work List Run results"""

    run_response: RunResponse
    worklist: WorkList


class ChecksRunner:
    """"ATC Checks runner"""

    def __init__(self, connection, variant):
        """:param connection: ADT Connection
           :param variant: A string holding the executed variant name
        """
        self._connection = connection
        self._variant = variant
        self._worklist_id = None

    def _get_id(self):
        """Fetches this list's ID"""

        if self._worklist_id is None:
            resp = self._connection.execute('POST', 'atc/worklists',
                                            params={'checkVariant': self._variant},
                                            accept='text/plain')
            self._worklist_id = resp.text

        return self._worklist_id

    def run_for(self, obj_sets, max_verdicts=100):
        """Executes checks for the given object sets"""

        run_request = RunRequest(obj_sets, max_verdicts)
        request = Marshal().serialize(run_request)

        worklist_id = self._get_id()
        resp = self._connection.execute('POST', 'atc/runs', params={'worklistId': worklist_id},
                                        accept='application/xml', content_type='application/xml',
                                        body=request)

        run_response = RunResponse()
        Marshal.deserialize(resp.text, run_response)

        resp = self._connection.execute('GET', f'atc/worklists/{worklist_id}',
                                        params={'includeExemptedFindings': 'false'},
                                        accept='application/atc.worklist.v1+xml')

        worklist = WorkList()
        Marshal.deserialize(resp.text, worklist)

        # increase all priorities by 1 to be in sync with SAPGui. ADT protocol sends priorities
        # decreased by one
        for obj in worklist.objects:
            for finding in obj.findings:
                # increment only if priority is integer
                try:
                    finding_number = int(finding.priority)
                    finding.priority = str(finding_number + 1)
                except ValueError:
                    pass

        return WorkListRunResult(run_response, worklist)


# pylint: disable=too-many-locals,too-many-nested-blocks,too-many-branches
def dump_profiles(connection, profiles=None, priorities=False, checkman=False):
    """Dump ATC profiles for the connected system"""

    result = {}

    # get list of profiles
    profiles = fetch_profiles(connection, profiles)

    # extend profiles of translations
    sqlconsole = DataPreview(connection)
    table = sqlconsole.execute("SELECT LANGU, CHKPRFID, TXTCHKPRF FROM CRMCHKPRFT WHERE LANGU = 'E'", rows=99999)
    for row in table:
        profile_id = row['CHKPRFID']
        # ignore tranlations for net existing profiles
        if profile_id not in profiles:
            continue

        profiles[profile_id]['description'] = row['TXTCHKPRF']

    # enhance profiles of checks
    table = sqlconsole.execute("SELECT CHKPRFID, CHKID, SEQNBR, SINCE, NOTE FROM CRMCHKPRF", rows=99999)
    for row in table:
        profile_id = row['CHKPRFID']
        # ignore tranlations for net existing profiles
        if profile_id not in profiles:
            continue

        if 'checks' not in profiles[profile_id]:
            profiles[profile_id]['checks'] = {}

        profiles[profile_id]['checks'][row['CHKID']] = {
            'sequence_number': row['SEQNBR'],
            'since': row['SINCE'],
            'note': row['NOTE']
        }

    result['profiles'] = profiles

    # enhance checks of analysis classes
    table = sqlconsole.execute("SELECT CHKID, CLCHK FROM CRMCHK", rows=99999)

    # loop through all profiles and checks and add list of priorities
    for profile in profiles.values():
        for check_id, check in profile['checks'].items():
            for row in table:
                if row['CHKID'] == check_id:
                    check['class'] = row['CLCHK']
                    break

    # enhance checks of descriptions
    table = sqlconsole.execute("SELECT CHKID, TXTCHK FROM CRMCHKT WHERE LANGU = 'E'", rows=99999)

    # loop through all profiles and checks and add list of priorities
    for profile in profiles.values():
        for check_id, check in profile['checks'].items():
            for row in table:
                if row['CHKID'] == check_id:
                    check['description'] = row['TXTCHK']
                    break

    if priorities:

        # fetch english descriptions for all check rules/messages
        chkmsgt = sqlconsole.execute("SELECT CHKID, CHKMSGID, TXTCHKMSG FROM CRMCHKMSGT WHERE LANGU = 'E'", rows=99999)

        # read all priorities from dedicated view (used by ATC engine during execution)
        computed_priorities = sqlconsole.execute(
            "SELECT CHKID, CHKMSGID, DEFAULTMSGPRIO, CHKMSGPRIO FROM CRM_CHECK_RULE",
            rows=99999)

        # loop through all profiles and checks and add list of priorities
        for profile in profiles.values():
            for check_id, check in profile['checks'].items():
                # look for priorities
                for row in computed_priorities:
                    if row['CHKID'] == check_id:
                        if 'priorities' not in check:
                            check['priorities'] = {}

                        check['priorities'][row['CHKMSGID']] = {
                            'check_message_id': row['CHKMSGID'],
                            'default_prio': row['DEFAULTMSGPRIO'],
                            'prio': row['CHKMSGPRIO']
                        }

                        # add description
                        desc = None
                        for d in chkmsgt:
                            if d['CHKID'] == row['CHKID'] and d['CHKMSGID'] == row['CHKMSGID']:
                                desc = d['TXTCHKMSG']
                                break
                        check['priorities'][row['CHKMSGID']]['description'] = desc if desc is not None else ''

    if checkman:
        # build set of all relevant check IDs
        check_ids = set()
        for profile in profiles.values():
            for check_id in profile['checks']:
                check_ids.add(check_id)

        # fetch check priorities
        result['checkman_messages'] = []
        table = sqlconsole.execute(
            "SELECT CHKID, CHKVIEW, CHKMSGID, DEFAULTMSGPRIO, CHKMSGPRIO FROM CRMCHKMSG",
            rows=99999)
        for row in table:
            # skip records for not relevant check ids (not used in any profile)
            if row['CHKID'] not in check_ids:
                continue

            result['checkman_messages'].append({
                'check_id': row['CHKID'],
                'check_view': row['CHKVIEW'],
                'check_message_id': row['CHKMSGID'],
                'default_prio': row['DEFAULTMSGPRIO'],
                'prio': row['CHKMSGPRIO']
            })

        # fetch check priorities
        result['checkman_messages_local'] = []
        table = sqlconsole.execute("SELECT CHKID, CHKVIEW, CHKMSGID, LOCAL_PRIO, "
                                   "DEACTIVATED, VALID_TO, VALID_ID FROM  CRMCHKMSG_LOCAL", rows=99999)
        for row in table:
            # skip records for not relevant check ids (not used in any profile)
            if row['CHKID'] not in check_ids:
                continue

            result['checkman_messages_local'].append({
                'check_id': row['CHKID'],
                'check_view': row['CHKVIEW'],
                'check_message_id': row['CHKMSGID'],
                'local_prio': row['LOCAL_PRIO'],
                'deactivated': row['DEACTIVATED'],
                'valid_to': row['VALID_TO'],
                'valid_id': row['VALID_ID']
            })

    return result


def fetch_profiles(connection, profiles=None):
    """Fetch ATC profiles for the connected system"""

    sqlconsole = DataPreview(connection)
    table = sqlconsole.execute("SELECT CHKPRFID, CRETSTAMP, CREUSER, CHGTSTAMP, CHGUSER FROM CRMCHKPRFH", rows=99999)

    result = {}

    for row in table:
        # if profile filtering is active then check current profile id
        # and skip all that are not part of filter
        if profiles is not None and row['CHKPRFID'] not in profiles:
            continue

        result[row['CHKPRFID']] = {
            "created": row['CRETSTAMP'],
            "created_by": row['CREUSER'],
            "changed": row['CHGTSTAMP'],
            "changed_by": row['CHGUSER']
        }

    return result
