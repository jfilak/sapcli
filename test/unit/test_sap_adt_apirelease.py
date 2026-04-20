#!/usr/bin/env python3

import unittest

import sap.adt.apirelease
from sap.adt.apirelease import ContractKey
from sap.adt.marshalling import Marshal

from mock import Connection, Response
from fixtures_adt_apirelease import (
    OBJECT_URI,
    API_RELEASE_RESPONSE_XML,
    VALIDATION_RESPONSE_INFO_XML,
    VALIDATION_RESPONSE_ERROR_XML,
    VALIDATION_RESPONSE_WARNING_XML,
    VALIDATION_RESPONSE_MULTIPLE_MESSAGES_XML,
    SET_API_RELEASE_RESPONSE_XML,
    VALIDATE_POST_BODY_XML,
)


class TestApiReleaseDeserialization(unittest.TestCase):

    def test_deserialization(self):
        result = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, result)

        # Releasable object
        self.assertEqual(result.releasable_object.uri, '/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat')
        self.assertEqual(result.releasable_object.typ, 'DDLS/DF')
        self.assertEqual(result.releasable_object.name, 'I_STATISTICALKEYFIGURECAT')

        # Behaviour
        self.assertEqual(result.behaviour.create, 'true')
        self.assertEqual(result.behaviour.comment_enabled, 'true')

        # Behaviour C0
        self.assertEqual(result.behaviour.c0_release.create, 'true')
        self.assertEqual(result.behaviour.c0_release.read, 'false')
        self.assertEqual(result.behaviour.c0_release.use_in_key_user_apps_read_only, 'true')
        self.assertEqual(result.behaviour.c0_release.use_in_sap_cloud_platform_default, 'true')

        # Behaviour C1
        self.assertEqual(result.behaviour.c1_release.read, 'true')
        self.assertEqual(result.behaviour.c1_release.update, 'true')
        self.assertEqual(result.behaviour.c1_release.delete, 'true')
        self.assertEqual(result.behaviour.c1_release.auth_values_enabled, 'true')

        # C0 contract
        self.assertEqual(result.c0_release.contract, 'C0')
        self.assertEqual(result.c0_release.use_in_key_user_apps, 'false')
        self.assertEqual(result.c0_release.use_in_sap_cloud_platform, 'false')
        self.assertEqual(result.c0_release.name, 'sap_bc_adt_ddic_ddl_sources_i_statisticalkeyfigurecat_C0')
        self.assertEqual(result.c0_release.status.state, 'NOT_RELEASED')
        self.assertEqual(result.c0_release.status.state_description, 'Not Released')
        self.assertEqual(result.c0_release.transport_object.typ, 'APIS')
        self.assertEqual(result.c0_release.transport_object.package_name, 'FINS_STSTCL_KEY_FIGURE_VDM')

        # C0 state transitions
        self.assertEqual(len(result.c0_release.state_transitions), 2)
        self.assertEqual(result.c0_release.state_transitions[0].state, 'NOT_RELEASED')
        self.assertEqual(result.c0_release.state_transitions[1].state, 'RELEASED')

        # C1 contract
        self.assertEqual(result.c1_release.contract, 'C1')
        self.assertEqual(result.c1_release.use_in_key_user_apps, 'true')
        self.assertEqual(result.c1_release.status.state, 'RELEASED')
        self.assertEqual(result.c1_release.status.state_description, 'Released')
        self.assertEqual(result.c1_release.changed_at, '2018-01-25T23:00:00Z')
        self.assertEqual(result.c1_release.changed_by, 'LIYI2')

        # C1 state transitions
        self.assertEqual(len(result.c1_release.state_transitions), 3)
        self.assertEqual(result.c1_release.state_transitions[0].state, 'RELEASED')
        self.assertEqual(result.c1_release.state_transitions[1].state, 'DEPRECATED')
        self.assertEqual(result.c1_release.state_transitions[2].state, 'NOT_RELEASED')

        # API catalog data
        self.assertEqual(result.api_catalog_data.is_any_assignment_possible, 'true')
        self.assertEqual(result.api_catalog_data.is_any_contract_released, 'true')

    def test_contracts_property(self):
        result = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, result)

        contracts = result.contracts
        self.assertEqual(len(contracts), 2)
        self.assertEqual(contracts[0].contract, 'C0')
        self.assertEqual(contracts[1].contract, 'C1')


class TestSetApiReleaseResponseDeserialization(unittest.TestCase):

    def test_deserialization_with_new_contract_fields(self):
        result = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(SET_API_RELEASE_RESPONSE_XML, result)

        self.assertEqual(result.c1_release.contract, 'C1')
        self.assertEqual(result.c1_release.use_in_key_user_apps, 'true')
        self.assertEqual(result.c1_release.use_in_sap_cloud_platform, 'true')
        self.assertEqual(result.c1_release.comment, 'This is a comment')
        self.assertEqual(result.c1_release.create_auth_values, 'true')
        self.assertEqual(result.c1_release.status.state, 'RELEASED')
        self.assertEqual(result.c1_release.changed_at, '2026-04-20T00:00:00Z')
        self.assertEqual(result.c1_release.changed_by, 'DEVELOPER')

        # New fields: useConceptAsSuccessor, successors, successorConceptName
        self.assertEqual(result.c1_release.use_concept_as_successor, 'false')
        self.assertIsNotNone(result.c1_release.successors)
        self.assertIsNotNone(result.c1_release.successor_concept_name)


class TestValidationDeserialization(unittest.TestCase):

    def test_deserialization_info_message(self):
        result = sap.adt.apirelease.ApiReleaseValidation()
        Marshal.deserialize(VALIDATION_RESPONSE_INFO_XML, result)

        self.assertEqual(result.releasable_object.name, 'I_STATISTICALKEYFIGURECAT')
        self.assertEqual(result.releasable_object.typ, 'DDLS/DF')

        self.assertEqual(len(result.validation_messages), 1)
        msg = result.validation_messages[0]
        self.assertEqual(msg.typ, 'I')
        self.assertEqual(msg.text, 'Changes are valid.')
        self.assertEqual(msg.msgid, 'ARS_ADT')
        self.assertEqual(msg.msgno, '002')
        self.assertEqual(msg.msgv1, '')

    def test_deserialization_error_message(self):
        result = sap.adt.apirelease.ApiReleaseValidation()
        Marshal.deserialize(VALIDATION_RESPONSE_ERROR_XML, result)

        self.assertEqual(len(result.validation_messages), 1)
        msg = result.validation_messages[0]
        self.assertEqual(msg.typ, 'E')
        self.assertEqual(msg.text, 'Contract C1 cannot be released.')
        self.assertEqual(msg.msgid, 'ARS_ADT')
        self.assertEqual(msg.msgno, '010')
        self.assertEqual(msg.msgv1, 'C1')

    def test_deserialization_warning_message(self):
        result = sap.adt.apirelease.ApiReleaseValidation()
        Marshal.deserialize(VALIDATION_RESPONSE_WARNING_XML, result)

        self.assertEqual(len(result.validation_messages), 1)
        msg = result.validation_messages[0]
        self.assertEqual(msg.typ, 'W')
        self.assertEqual(msg.text, 'Object has open changes.')

    def test_deserialization_multiple_messages(self):
        result = sap.adt.apirelease.ApiReleaseValidation()
        Marshal.deserialize(VALIDATION_RESPONSE_MULTIPLE_MESSAGES_XML, result)

        self.assertEqual(len(result.validation_messages), 2)
        self.assertEqual(result.validation_messages[0].typ, 'I')
        self.assertEqual(result.validation_messages[1].typ, 'W')


class TestGetApiRelease(unittest.TestCase):

    def test_get_api_release(self):
        conn = Connection([Response(status_code=200,
                                    content_type='application/vnd.sap.adt.apirelease.v11+xml',
                                    text=API_RELEASE_RESPONSE_XML)])

        result = sap.adt.apirelease.get_api_release(conn, OBJECT_URI)

        self.assertEqual(len(conn.execs), 1)
        req = conn.execs[0]
        self.assertEqual(req.method, 'GET')
        self.assertIn('apireleases/', req.adt_uri)
        self.assertEqual(req.headers['Accept'], ', '.join(sap.adt.apirelease.ACCEPT_MIME_TYPES))

        self.assertEqual(result.releasable_object.name, 'I_STATISTICALKEYFIGURECAT')
        self.assertEqual(result.c0_release.status.state, 'NOT_RELEASED')
        self.assertEqual(result.c1_release.status.state, 'RELEASED')


class TestValidateApiRelease(unittest.TestCase):

    def test_validate_api_release_info(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apireleasecontractvalidation.v2+xml',
            text=VALIDATION_RESPONSE_INFO_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        result = sap.adt.apirelease.validate_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        self.assertEqual(len(conn.execs), 1)
        req = conn.execs[0]
        self.assertEqual(req.method, 'POST')
        self.assertIn('apireleases/', req.adt_uri)
        self.assertIn('/c1/validationrun', req.adt_uri)
        self.assertEqual(
            req.headers['Content-Type'],
            sap.adt.apirelease.ApiReleaseValidation.objtype.mimetype
        )
        self.assertEqual(
            req.headers['Accept'],
            ', '.join(sap.adt.apirelease.VALIDATION_ACCEPT_MIME_TYPES)
        )
        self.assertIsNotNone(req.body)

        self.assertEqual(result.releasable_object.name, 'I_STATISTICALKEYFIGURECAT')
        self.assertEqual(len(result.validation_messages), 1)
        self.assertEqual(result.validation_messages[0].typ, 'I')

    def test_validate_api_release_error(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apireleasecontractvalidation.v2+xml',
            text=VALIDATION_RESPONSE_ERROR_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        result = sap.adt.apirelease.validate_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        self.assertEqual(len(result.validation_messages), 1)
        self.assertEqual(result.validation_messages[0].typ, 'E')

    def test_validate_api_release_uri_encoding(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apireleasecontractvalidation.v2+xml',
            text=VALIDATION_RESPONSE_INFO_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        sap.adt.apirelease.validate_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        req = conn.execs[0]
        self.assertIn('/c1/validationrun', req.adt_uri)
        # object URI should be percent-encoded
        self.assertIn('%2F', req.adt_uri)


    def test_validate_api_release_post_body(self):
        """The POST body sent to validate must exactly match the expected XML"""
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apireleasecontractvalidation.v2+xml',
            text=VALIDATION_RESPONSE_INFO_XML
        )])

        api_release = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, api_release)

        # Build the payload the same way _build_payload does in the CLI
        target = api_release.copy_contract(ContractKey.C1)
        target.status.state_description = None

        payload = sap.adt.apirelease.ApiRelease()
        payload.c1_release = target
        payload.api_catalog_data = api_release.api_catalog_data

        sap.adt.apirelease.validate_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        req = conn.execs[0]
        self.assertEqual(req.body, VALIDATE_POST_BODY_XML)


class TestSetApiRelease(unittest.TestCase):

    def test_set_api_release_with_corrnr(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apirelease.v11+xml',
            text=SET_API_RELEASE_RESPONSE_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        result = sap.adt.apirelease.set_api_release(
            conn, OBJECT_URI, ContractKey.C1, payload, corrnr='C50K000061'
        )

        self.assertEqual(len(conn.execs), 1)
        req = conn.execs[0]
        self.assertEqual(req.method, 'PUT')
        self.assertIn('apireleases/', req.adt_uri)
        self.assertIn('/c1', req.adt_uri)
        self.assertNotIn('validationrun', req.adt_uri)
        self.assertEqual(
            req.headers['Content-Type'],
            sap.adt.apirelease.ACCEPT_MIME_TYPES[0]
        )
        self.assertEqual(
            req.headers['Accept'],
            ', '.join(sap.adt.apirelease.ACCEPT_MIME_TYPES)
        )
        self.assertEqual(req.params, {'request': 'C50K000061'})
        self.assertIsNotNone(req.body)

        self.assertEqual(result.c1_release.contract, 'C1')
        self.assertEqual(result.c1_release.status.state, 'RELEASED')
        self.assertEqual(result.c1_release.comment, 'This is a comment')

    def test_set_api_release_without_corrnr(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apirelease.v11+xml',
            text=SET_API_RELEASE_RESPONSE_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        sap.adt.apirelease.set_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        req = conn.execs[0]
        self.assertIsNone(req.params)

    def test_set_api_release_uri_encoding(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apirelease.v11+xml',
            text=SET_API_RELEASE_RESPONSE_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        sap.adt.apirelease.set_api_release(conn, OBJECT_URI, ContractKey.C1, payload)

        req = conn.execs[0]
        self.assertTrue(req.adt_uri.endswith('/c1'))
        # object URI should be percent-encoded
        self.assertIn('%2F', req.adt_uri)

    def test_set_api_release_response_deserialization(self):
        conn = Connection([Response(
            status_code=200,
            content_type='application/vnd.sap.adt.apirelease.v11+xml',
            text=SET_API_RELEASE_RESPONSE_XML
        )])

        payload = sap.adt.apirelease.ApiRelease()
        result = sap.adt.apirelease.set_api_release(
            conn, OBJECT_URI, ContractKey.C1, payload, corrnr='C50K000061'
        )

        # Verify full deserialization of the update response
        self.assertEqual(result.releasable_object.name, 'I_STATISTICALKEYFIGURECAT')
        self.assertEqual(result.behaviour.create, 'true')
        self.assertEqual(result.c1_release.use_in_key_user_apps, 'true')
        self.assertEqual(result.c1_release.use_in_sap_cloud_platform, 'true')
        self.assertEqual(result.c1_release.use_concept_as_successor, 'false')
        self.assertEqual(result.api_catalog_data.is_any_contract_released, 'true')


class TestApiReleaseGetContract(unittest.TestCase):

    def setUp(self):
        self.api_release = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, self.api_release)

    def test_get_contract_existing(self):
        contract = self.api_release.get_contract(ContractKey.C1)
        self.assertIsNotNone(contract)
        self.assertEqual(contract.contract, 'C1')

    def test_get_contract_not_set(self):
        contract = self.api_release.get_contract(ContractKey.C3)
        self.assertIsNone(contract)

    def test_get_contract_behaviour_existing(self):
        behaviour = self.api_release.get_contract_behaviour(ContractKey.C1)
        self.assertIsNotNone(behaviour)
        self.assertEqual(behaviour.create, 'false')
        self.assertEqual(behaviour.read, 'true')

    def test_get_contract_behaviour_not_set(self):
        behaviour = self.api_release.get_contract_behaviour(ContractKey.C3)
        self.assertIsNone(behaviour)

    def test_get_contract_behaviour_no_behaviour(self):
        empty = sap.adt.apirelease.ApiRelease()
        self.assertIsNone(empty.get_contract_behaviour(ContractKey.C1))

    def test_copy_contract_existing(self):
        copy = self.api_release.copy_contract(ContractKey.C1)
        self.assertEqual(copy.contract, 'C1')
        self.assertEqual(copy.use_in_key_user_apps, 'true')
        self.assertEqual(copy.use_in_sap_cloud_platform, 'false')
        self.assertEqual(copy.comment, '')
        self.assertEqual(copy.status.state, 'RELEASED')
        self.assertEqual(copy.status.state_description, 'Released')

    def test_copy_contract_not_set(self):
        copy = self.api_release.copy_contract(ContractKey.C3)
        self.assertEqual(copy.contract, 'C3')
        self.assertIsNotNone(copy.status)

    def test_copy_contract_existing_no_status(self):
        """Copy a contract that exists but has no status"""
        self.api_release.c0_release.status = None
        copy = self.api_release.copy_contract(ContractKey.C0)
        self.assertEqual(copy.contract, 'C0')
        self.assertIsNone(copy.status)


class TestContractKey(unittest.TestCase):

    def test_attr_name(self):
        self.assertEqual(ContractKey.C0.attr_name, 'c0_release')
        self.assertEqual(ContractKey.C4.attr_name, 'c4_release')

    def test_all_values(self):
        self.assertEqual(
            [k.value for k in ContractKey],
            ['c0', 'c1', 'c2', 'c3', 'c4']
        )

    def test_from_string(self):
        self.assertEqual(ContractKey('c1'), ContractKey.C1)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            ContractKey('c9')


class TestContractDefaults(unittest.TestCase):
    """Test that a freshly created Contract has the correct default attribute values"""

    def test_contract_default_values(self):
        contract = sap.adt.apirelease.Contract()
        self.assertEqual(contract.use_in_key_user_apps, 'false')
        self.assertEqual(contract.use_in_sap_cloud_platform, 'false')
        self.assertEqual(contract.comment, '')
        self.assertEqual(contract.feature_toggle, '')
        self.assertEqual(contract.create_auth_values, 'false')
        self.assertEqual(contract.use_concept_as_successor, 'false')
        self.assertIsNone(contract.contract)
        self.assertIsNone(contract.name)
        self.assertIsNone(contract.status)
        self.assertIsNone(contract.state_transitions)
        self.assertIsNone(contract.transport_object)


class TestApiReleaseSerialization(unittest.TestCase):
    """Verify that serialized XML payloads match the format expected by the ABAP handler"""

    def _serialize(self, obj):
        return Marshal().serialize(obj)

    def test_empty_api_release_no_empty_tags(self):
        """An empty ApiRelease must not emit empty child elements for ignore_empty fields"""
        payload = sap.adt.apirelease.ApiRelease()
        xml = self._serialize(payload)

        self.assertNotIn('<ars:releasableObject/>', xml)
        self.assertNotIn('<ars:behaviour/>', xml)
        self.assertNotIn('<ars:c0Release/>', xml)
        self.assertNotIn('<ars:c1Release/>', xml)
        self.assertNotIn('<ars:c2Release/>', xml)
        self.assertNotIn('<ars:c3Release/>', xml)
        self.assertNotIn('<ars:c4Release/>', xml)

    def test_contract_no_empty_state_transitions_or_transport(self):
        """Contract with no state_transitions/transport_object must not emit empty tags"""
        payload = sap.adt.apirelease.ApiRelease()
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C1'
        contract.status = sap.adt.apirelease.ContractStatus()
        contract.status.state = 'RELEASED'
        payload.c1_release = contract
        xml = self._serialize(payload)

        self.assertNotIn('<ars:stateTransitions/>', xml)
        self.assertNotIn('<ars:transportObject/>', xml)

    def test_contract_default_attributes_in_xml(self):
        """Contract defaults must appear as attributes in the serialized XML"""
        payload = sap.adt.apirelease.ApiRelease()
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C1'
        contract.status = sap.adt.apirelease.ContractStatus()
        contract.status.state = 'RELEASED'
        payload.c1_release = contract
        xml = self._serialize(payload)

        self.assertIn('ars:useInKeyUserApps="false"', xml)
        self.assertIn('ars:useInSAPCloudPlatform="false"', xml)
        self.assertIn('ars:comment=""', xml)
        self.assertIn('ars:featureToggle=""', xml)
        self.assertIn('ars:createAuthValues="false"', xml)

    def test_status_state_uppercase_no_description(self):
        """Status must have uppercase state and can omit stateDescription when None"""
        payload = sap.adt.apirelease.ApiRelease()
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C1'
        contract.status = sap.adt.apirelease.ContractStatus()
        contract.status.state = 'RELEASED'
        contract.status.state_description = None
        payload.c1_release = contract
        xml = self._serialize(payload)

        self.assertIn('ars:state="RELEASED"', xml)
        self.assertNotIn('ars:stateDescription', xml)

    def test_api_catalog_data_includes_api_catalogs(self):
        """ApiCatalogData must include ars:ApiCatalogs element"""
        payload = sap.adt.apirelease.ApiRelease()
        payload.api_catalog_data = sap.adt.apirelease.ApiCatalogData()
        payload.api_catalog_data.is_any_assignment_possible = 'true'
        payload.api_catalog_data.is_any_contract_released = 'true'
        xml = self._serialize(payload)

        self.assertIn('ars:ApiCatalogs', xml)

    def test_validate_payload_structure(self):
        """Simulate the payload built for validate: contract + api_catalog_data only"""
        api_release = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, api_release)

        # Simulate _build_payload: copy contract, clear description, set state
        target = api_release.copy_contract(ContractKey.C1)
        target.status.state_description = None
        target.status.state = 'RELEASED'

        payload = sap.adt.apirelease.ApiRelease()
        payload.c1_release = target
        payload.api_catalog_data = api_release.api_catalog_data

        xml = self._serialize(payload)

        # Must NOT contain empty tags for unused top-level fields
        self.assertNotIn('<ars:releasableObject', xml)
        self.assertNotIn('<ars:behaviour', xml)
        self.assertNotIn('<ars:c0Release', xml)

        # Must contain c1Release with correct attributes
        self.assertIn('ars:contract="C1"', xml)
        self.assertIn('ars:state="RELEASED"', xml)
        self.assertNotIn('ars:stateDescription', xml)

        # Must contain api catalog data with ApiCatalogs
        self.assertIn('<ars:apiCatalogData', xml)
        self.assertIn('ars:ApiCatalogs', xml)

        # Contract defaults must be present
        self.assertIn('ars:comment=""', xml)
        self.assertIn('ars:createAuthValues="false"', xml)

        # No empty state_transitions or transport_object (copy_contract doesn't copy them)
        self.assertNotIn('<ars:stateTransitions', xml)
        self.assertNotIn('<ars:transportObject', xml)

    def test_set_payload_structure(self):
        """Simulate the payload built for set: same as validate"""
        api_release = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, api_release)

        target = api_release.copy_contract(ContractKey.C1)
        target.status.state_description = None
        target.status.state = 'DEPRECATED'
        target.comment = 'Deprecating this API'
        target.use_in_sap_cloud_platform = 'true'

        payload = sap.adt.apirelease.ApiRelease()
        payload.c1_release = target
        payload.api_catalog_data = api_release.api_catalog_data

        xml = self._serialize(payload)

        self.assertIn('ars:state="DEPRECATED"', xml)
        self.assertNotIn('ars:stateDescription', xml)
        self.assertIn('ars:comment="Deprecating this API"', xml)
        self.assertIn('ars:useInSAPCloudPlatform="true"', xml)
        self.assertIn('ars:useInKeyUserApps="true"', xml)  # copied from existing
        self.assertIn('ars:ApiCatalogs', xml)
        self.assertNotIn('<ars:stateTransitions', xml)
        self.assertNotIn('<ars:transportObject', xml)


if __name__ == '__main__':
    unittest.main()
