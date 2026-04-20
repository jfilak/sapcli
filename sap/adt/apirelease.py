"""ADT API Release functionality

Types and functions for getting API release contract information of ABAP objects.

Usage:

    connection = sap.adt.Connection(...)
    ddl = sap.adt.DataDefinition(connection, 'I_STATISTICALKEYFIGURECAT')
    result = sap.adt.apirelease.get_api_release(connection, ddl.full_adt_uri)
    for contract in result.contracts:
        print(contract.contract, contract.status.state, contract.status.state_description)
"""

from typing import Optional
from enum import Enum

from urllib.parse import quote

from sap.adt.core import Connection
from sap.adt.objects import OrderedClassMembers, ADTObjectType, XMLNamespace
from sap.adt.annotations import XmlNodeAttributeProperty, XmlNodeProperty, XmlContainer, xml_text_node_property
from sap.adt.marshalling import Marshal


XMLNS_ARS = XMLNamespace('ars', 'http://www.sap.com/adt/ars')

VALIDATION_ACCEPT_MIME_TYPES = [
    'application/vnd.sap.adt.apireleasecontractvalidation+xml',
    'application/vnd.sap.adt.apireleasecontractvalidation.v2+xml',
]

ACCEPT_MIME_TYPES = [
    'application/vnd.sap.adt.apirelease.v11+xml',
    'application/vnd.sap.adt.apirelease.v10+xml',
    'application/vnd.sap.adt.apirelease.v9+xml',
    'application/vnd.sap.adt.apirelease.v8+xml',
    'application/vnd.sap.adt.apirelease.v7+xml',
    'application/vnd.sap.adt.apirelease.v6+xml',
    'application/vnd.sap.adt.apirelease.v5+xml',
    'application/vnd.sap.adt.apirelease.v4+xml',
    'application/vnd.sap.adt.apirelease.v3+xml',
    'application/vnd.sap.adt.apirelease.v2+xml',
    'application/vnd.sap.adt.apirelease+xml',
]


class ContractKey(Enum):
    """Contract level identifiers (C0-C4) for API release management"""

    C0 = 'c0'
    C1 = 'c1'
    C2 = 'c2'
    C3 = 'c3'
    C4 = 'c4'

    @property
    def attr_name(self):
        """Returns the attribute name for this contract on ApiRelease/Behaviour (e.g. 'c1_release')"""

        return f'{self.value}_release'


# pylint: disable=too-few-public-methods
class ReleasableObject(metaclass=OrderedClassMembers):
    """The ADT object for which the API release information is provided"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')


# pylint: disable=too-few-public-methods
class ContractBehaviour(metaclass=OrderedClassMembers):
    """Behaviour flags for a specific contract level (C0-C4)"""

    create = XmlNodeAttributeProperty('ars:create')
    read = XmlNodeAttributeProperty('ars:read')
    update = XmlNodeAttributeProperty('ars:update')
    delete = XmlNodeAttributeProperty('ars:delete')
    use_in_key_user_apps_default = XmlNodeAttributeProperty('ars:useInKeyUserAppsDefault')
    use_in_key_user_apps_read_only = XmlNodeAttributeProperty('ars:useInKeyUserAppsReadOnly')
    # pylint: disable=invalid-name
    use_in_sap_cloud_platform_default = XmlNodeAttributeProperty('ars:useInSAPCloudPlatformDefault')
    # pylint: disable=invalid-name
    use_in_sap_cloud_platform_read_only = XmlNodeAttributeProperty('ars:useInSAPCloudPlatformReadOnly')
    auth_values_enabled = XmlNodeAttributeProperty('ars:authValuesEnabled')


# pylint: disable=too-few-public-methods
class Behaviour(metaclass=OrderedClassMembers):
    """Overall behaviour of the API release object"""

    create = XmlNodeAttributeProperty('ars:create')
    comment_enabled = XmlNodeAttributeProperty('ars:commentEnabled')
    c0_release = XmlNodeProperty('ars:c0Release', factory=ContractBehaviour)
    c1_release = XmlNodeProperty('ars:c1Release', factory=ContractBehaviour)
    c2_release = XmlNodeProperty('ars:c2Release', factory=ContractBehaviour)
    c3_release = XmlNodeProperty('ars:c3Release', factory=ContractBehaviour)
    c4_release = XmlNodeProperty('ars:c4Release', factory=ContractBehaviour)


# pylint: disable=too-few-public-methods
class ContractStatus(metaclass=OrderedClassMembers):
    """State and description of a contract"""

    state = XmlNodeAttributeProperty('ars:state')
    state_description = XmlNodeAttributeProperty('ars:stateDescription')


# pylint: disable=invalid-name
ContractStatusList = XmlContainer.define('ars:status', ContractStatus)


# pylint: disable=too-few-public-methods
class TransportObject(metaclass=OrderedClassMembers):
    """Transport object reference"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')
    package_name = XmlNodeAttributeProperty('adtcore:packageName')


# pylint: disable=too-few-public-methods
class Contract(metaclass=OrderedClassMembers):
    """A single contract level (C0, C1, C2, etc.) with its release status"""

    contract = XmlNodeAttributeProperty('ars:contract')
    use_in_key_user_apps = XmlNodeAttributeProperty('ars:useInKeyUserApps', value="false")
    use_in_sap_cloud_platform = XmlNodeAttributeProperty('ars:useInSAPCloudPlatform', value="false")
    comment = XmlNodeAttributeProperty('ars:comment', value="")
    feature_toggle = XmlNodeAttributeProperty('ars:featureToggle', value="")
    create_auth_values = XmlNodeAttributeProperty('ars:createAuthValues', value="false")
    name = XmlNodeAttributeProperty('adtcore:name')
    changed_at = XmlNodeAttributeProperty('adtcore:changedAt')
    changed_by = XmlNodeAttributeProperty('adtcore:changedBy')
    status = XmlNodeProperty('ars:status', factory=ContractStatus)
    use_concept_as_successor = xml_text_node_property('ars:useConceptAsSuccessor', value="false")
    successors = xml_text_node_property('ars:successors')
    successor_concept_name = xml_text_node_property('ars:successorConceptName')
    state_transitions = XmlNodeProperty('ars:stateTransitions', factory=ContractStatusList, ignore_empty=True)
    transport_object = XmlNodeProperty('ars:transportObject', factory=TransportObject, ignore_empty=True)


# pylint: disable=too-few-public-methods
class ApiCatalogData(metaclass=OrderedClassMembers):
    """API catalog data"""

    is_any_assignment_possible = XmlNodeAttributeProperty('ars:isAnyAssignmentPossible')
    is_any_contract_released = XmlNodeAttributeProperty('ars:isAnyContractReleased')
    # Dummy property I don't know what should hold because I have no test data.
    api_catalogs = xml_text_node_property('ars:ApiCatalogs')


# pylint: disable=too-few-public-methods
class ApiRelease(metaclass=OrderedClassMembers):
    """Root API Release object containing all contract information"""

    objtype = ADTObjectType(None, 'apireleases', XMLNS_ARS, ACCEPT_MIME_TYPES, None, 'apiRelease')

    releasable_object = XmlNodeProperty('ars:releasableObject', factory=ReleasableObject, ignore_empty=True)
    behaviour = XmlNodeProperty('ars:behaviour', factory=Behaviour, ignore_empty=True)
    c0_release = XmlNodeProperty('ars:c0Release', factory=Contract, ignore_empty=True)
    c1_release = XmlNodeProperty('ars:c1Release', factory=Contract, ignore_empty=True)
    c2_release = XmlNodeProperty('ars:c2Release', factory=Contract, ignore_empty=True)
    c3_release = XmlNodeProperty('ars:c3Release', factory=Contract, ignore_empty=True)
    c4_release = XmlNodeProperty('ars:c4Release', factory=Contract, ignore_empty=True)
    api_catalog_data = XmlNodeProperty('ars:apiCatalogData', factory=ApiCatalogData)

    @property
    def contracts(self):
        """Returns a list of non-None contract releases"""

        result = []
        for key in ContractKey:
            attr = getattr(self, key.attr_name)
            if attr is not None and attr.contract is not None:
                result.append(attr)
        return result

    def get_contract(self, contract_key: ContractKey) -> Optional[Contract]:
        """Get the contract for the given key (c0-c4)"""

        return getattr(self, contract_key.attr_name)

    def get_contract_behaviour(self, contract_key: ContractKey) -> Optional[ContractBehaviour]:
        """Get the behaviour for the given contract key (c0-c4)"""

        if self.behaviour is None:
            return None

        return getattr(self.behaviour, contract_key.attr_name)

    def copy_contract(self, contract_key: ContractKey) -> Contract:
        """Create a copy of the existing contract for the given key, or a blank one if not set"""

        existing = self.get_contract(contract_key)
        target = Contract()

        if existing is not None and existing.contract is not None:
            target.contract = existing.contract
            target.use_in_key_user_apps = existing.use_in_key_user_apps
            target.use_in_sap_cloud_platform = existing.use_in_sap_cloud_platform
            target.comment = existing.comment
            if existing.status is not None:
                target.status = ContractStatus()
                target.status.state = existing.status.state
                target.status.state_description = existing.status.state_description
        else:
            target.contract = contract_key.value.upper()
            target.status = ContractStatus()

        return target


# pylint: disable=too-few-public-methods
class ValidationMessage(metaclass=OrderedClassMembers):
    """A single validation message returned by the validate endpoint"""

    typ = XmlNodeAttributeProperty('type')
    text = XmlNodeAttributeProperty('text')
    msgid = XmlNodeAttributeProperty('msgid')
    msgno = XmlNodeAttributeProperty('msgno')
    msgv1 = XmlNodeAttributeProperty('msgv1')
    msgv2 = XmlNodeAttributeProperty('msgv2')
    msgv3 = XmlNodeAttributeProperty('msgv3')
    msgv4 = XmlNodeAttributeProperty('msgv4')


# pylint: disable=invalid-name
ValidationMessageList = XmlContainer.define('ars:validationMessage', ValidationMessage)


# pylint: disable=too-few-public-methods
class ApiReleaseValidation(metaclass=OrderedClassMembers):
    """Root object for API release contract validation response"""

    objtype = ADTObjectType(None, 'apireleases', XMLNS_ARS,
                            VALIDATION_ACCEPT_MIME_TYPES, None, 'apiRelease')

    releasable_object = XmlNodeProperty('ars:releasableObject', factory=ReleasableObject)
    validation_messages = XmlNodeProperty('ars:validationMessages', factory=ValidationMessageList)


def get_api_release(connection: Connection, object_uri: str) -> ApiRelease:
    """Fetch API release information for the given ABAP object.

    Parameters:
        connection: ADT connection
        object_uri: full ADT URI of the object, e.g.
                    /sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat
                    most sapcli ADT objects have the full_adt_uri property that can be used here
    """

    encoded_uri = quote(object_uri, safe='')

    resp = connection.execute(
        'GET',
        f'{ApiRelease.objtype.basepath}/{encoded_uri}',
        accept=ApiRelease.objtype.all_mimetypes
    )

    result = ApiRelease()
    Marshal.deserialize(resp.text, result)
    return result


def validate_api_release(connection: Connection, object_uri: str,
                         contract: ContractKey, payload: ApiRelease) -> ApiReleaseValidation:
    """Validate API release contract changes before applying them.

    Parameters:
        connection: ADT connection
        object_uri: full ADT URI of the object
        contract: contract level (e.g. ContractKey.C1)
        payload: ApiRelease object containing the contract to validate

    Returns:
        ApiReleaseValidation with validation messages
    """

    encoded_uri = quote(object_uri, safe='')
    xml_body = Marshal().serialize(payload)

    resp = connection.execute(
        'POST',
        f'{ApiReleaseValidation.objtype.basepath}/{encoded_uri}/{contract.value}/validationrun',
        content_type=ApiReleaseValidation.objtype.mimetype,
        accept=ApiReleaseValidation.objtype.all_mimetypes,
        body=xml_body
    )

    result = ApiReleaseValidation()
    Marshal.deserialize(resp.text, result)
    return result


def set_api_release(connection: Connection, object_uri: str,
                    contract: ContractKey, payload: ApiRelease,
                    corrnr: Optional[str] = None) -> ApiRelease:
    """Update an API release contract for the given ABAP object.

    Parameters:
        connection: ADT connection
        object_uri: full ADT URI of the object
        contract: contract level (e.g. ContractKey.C1)
        payload: ApiRelease object containing the contract to update
        corrnr: optional transport request number

    Returns:
        Updated ApiRelease object
    """

    encoded_uri = quote(object_uri, safe='')
    xml_body = Marshal().serialize(payload)

    params = None
    if corrnr is not None:
        params = {'request': corrnr}

    resp = connection.execute(
        'PUT',
        f'{ApiRelease.objtype.basepath}/{encoded_uri}/{contract.value}',
        content_type=ApiRelease.objtype.mimetype,
        accept=ApiRelease.objtype.all_mimetypes,
        body=xml_body,
        params=params
    )

    result = ApiRelease()
    Marshal.deserialize(resp.text, result)
    return result
