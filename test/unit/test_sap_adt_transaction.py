#!/usr/bin/env python3

import json
import unittest
import sap.adt
import sap.adt.transaction
from sap.adt.transaction import (
    ReportTransactionDefinition,
    ParameterTransactionDefinition,
    DialogTransactionDefinition,
    OOTransactionDefinition,
    VariantTransactionDefinition,
)

from mock import Connection, Response, Request
from fixtures_adt_transaction import (
    TRANSACTION_NAME,
    TRANSACTION_DEFINITION_ADT_XML,
    CREATE_TRANSACTION_ADT_XML,
    REPORT_TRANSACTION_CREATION_JSON,
    CREATE_TRANSACTION_WITH_CONTENT_ADT_XML,
    PARAMETER_TRANSACTION_NAME,
    PARAMETER_TRANSACTION_CREATION_JSON,
)


class TestADTTransaction(unittest.TestCase):

    def test_transaction_fetch(self):
        connection = Connection([Response(text=TRANSACTION_DEFINITION_ADT_XML, status_code=200, headers={})])

        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME)
        transaction.fetch()

        self.assertEqual(transaction.name, TRANSACTION_NAME)
        self.assertEqual(transaction.master_language, 'EN')
        self.assertEqual(transaction.description, 'abapgit')
        self.assertEqual(transaction.objtype.code, 'TRAN/T')

    def test_transaction_serialize(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/aps/iam/tran',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.blues.v2+xml; charset=utf-8'},
            body=bytes(CREATE_TRANSACTION_ADT_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)

    def test_transaction_uri(self):
        connection = Connection()
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME)

        self.assertEqual(transaction.uri, 'aps/iam/tran/zabapgit')

    def test_transaction_without_package(self):
        connection = Connection()
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME)

        self.assertIsNone(transaction.reference.name)

    def test_transaction_with_package(self):
        connection = Connection()
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP')

        self.assertEqual(transaction.reference.name, '$TMP')

    def test_transaction_objtype(self):
        transaction = sap.adt.Transaction(Connection(), TRANSACTION_NAME)

        self.assertEqual(transaction.objtype.code, 'TRAN/T')
        self.assertEqual(transaction.objtype.basepath, 'aps/iam/tran')

    def test_transaction_source_uri(self):
        transaction = sap.adt.Transaction(Connection(), TRANSACTION_NAME)

        source_uri = transaction.objtype.get_uri_for_type('application/json')
        self.assertEqual(source_uri, '/source/main')

    def test_transaction_create_with_corrnr(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'
        transaction.definition.report_transaction = ReportTransactionDefinition(
            report_name='ZABAPGIT', report_dynnr='1000'
        )
        transaction.create(corrnr='C50K000001')

        self.assertEqual(connection.execs[0].params, {'corrNr': 'C50K000001'})


class TestTransactionCreationContent(unittest.TestCase):

    def test_build_report_transaction_creation_content(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'
        transaction.definition.report_transaction = ReportTransactionDefinition(
            report_name='ZABAPGIT', report_dynnr='1000'
        )

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)

        self.assertEqual(json.loads(content), json.loads(REPORT_TRANSACTION_CREATION_JSON))

    def test_build_parameter_transaction_creation_content(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='test jakub', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, PARAMETER_TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'parameterTransaction'
        transaction.definition.parameter_transaction = ParameterTransactionDefinition(
            par_parent_transaction_code='/AIF/28000003'
        )

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)

        self.assertEqual(json.loads(content), json.loads(PARAMETER_TRANSACTION_CREATION_JSON))

    def test_build_dialog_transaction_creation_content(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='dialog test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZDIALOG', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'dialogTransaction'
        transaction.definition.dialog_transaction = DialogTransactionDefinition(
            program_name='SAPMTEST', program_dynnr='0100'
        )

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['transactionType'], 'dialogTransaction')
        self.assertEqual(parsed['programName'], 'SAPMTEST')
        self.assertEqual(parsed['programDynnr'], '0100')
        self.assertEqual(parsed['metadata']['name'], 'ZDIALOG')

    def test_build_oo_transaction_creation_content(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='oo test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZOO_TRAN', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'ooTransaction'
        transaction.definition.oo_transaction = OOTransactionDefinition(
            class_name='ZCL_TEST', method_name='EXECUTE',
            oo_transaction_model=True
        )
        transaction.definition.update_mode = 'synchronous'

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['transactionType'], 'ooTransaction')
        self.assertEqual(parsed['className'], 'ZCL_TEST')
        self.assertEqual(parsed['methodName'], 'EXECUTE')
        self.assertTrue(parsed['ooTransactionModelIndi'])
        self.assertEqual(parsed['updateMode'], 'synchronous')

    def test_build_variant_transaction_creation_content(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='variant test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZVARIANT', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'variantTransaction'
        transaction.definition.variant_transaction = VariantTransactionDefinition(
            var_parent_transaction_code='MM01',
            transaction_variant_cross_client=True,
            transaction_variant_name='ZVAR01'
        )

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['transactionType'], 'variantTransaction')
        self.assertEqual(parsed['varParentTransactionCode'], 'MM01')
        self.assertTrue(parsed['transactionVariantCiIndi'])
        self.assertEqual(parsed['transactionCiVariantName'], 'ZVAR01')

    def test_creation_properties_not_in_serialized_xml(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'
        transaction.definition.report_transaction = ReportTransactionDefinition(
            report_name='ZABAPGIT', report_dynnr='1000'
        )

        xml, _ = transaction.serialize()

        self.assertNotIn('reportTransaction', xml)
        self.assertNotIn('reportName', xml)
        self.assertNotIn('reportDynnr', xml)
        self.assertNotIn('additionalCreationProperties', xml)

    def test_create_from_properties(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, TRANSACTION_NAME, package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'
        transaction.definition.report_transaction = ReportTransactionDefinition(
            report_name='ZABAPGIT', report_dynnr='1000'
        )

        transaction.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/aps/iam/tran',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.blues.v2+xml; charset=utf-8'},
            body=bytes(CREATE_TRANSACTION_WITH_CONTENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)

    def test_default_abap_language_version(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZTEST', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['abapLanguVersionText'], 'Standard ABAP')

    def test_custom_abap_language_version(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZTEST', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'
        transaction.definition.abap_language_version_text = 'ABAP for Cloud Development'

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['abapLanguVersionText'], 'ABAP for Cloud Development')

    def test_default_update_mode(self):
        connection = Connection()
        metadata = sap.adt.ADTCoreData(description='test', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction(connection, 'ZTEST', package='$TMP', metadata=metadata)
        transaction.definition.transaction_type = 'reportTransaction'

        content = transaction.definition.to_create_json(transaction.name, transaction.description,
                                                 transaction.reference.name)
        parsed = json.loads(content)

        self.assertEqual(parsed['updateMode'], 'notSet')


class TestTransactionFactory(unittest.TestCase):

    def _assert_common(self, transaction, name, description, package):
        self.assertEqual(transaction.name, name)
        self.assertEqual(transaction.description, description)
        self.assertEqual(transaction.reference.name, package)

    def test_report_transaction(self):
        conn = Connection()
        transaction = sap.adt.Transaction.report(
            conn, 'ZTRAN', description='desc', package='$TMP',
            report_name='ZREPORT', report_dynnr='1000'
        )

        self._assert_common(transaction, 'ZTRAN', 'desc', '$TMP')
        self.assertEqual(transaction.definition.transaction_type, 'reportTransaction')
        self.assertEqual(transaction.definition.report_transaction.report_name, 'ZREPORT')
        self.assertEqual(transaction.definition.report_transaction.report_dynnr, '1000')

    def test_report_transaction_with_variant(self):
        conn = Connection()
        transaction = sap.adt.Transaction.report(
            conn, 'ZTRAN', description='desc', package='$TMP',
            report_name='ZREPORT', report_dynnr='1000',
            report_variant_name='VAR1'
        )

        self.assertEqual(transaction.definition.report_transaction.report_variant_name, 'VAR1')

    def test_parameter_transaction(self):
        conn = Connection()
        transaction = sap.adt.Transaction.parameter(
            conn, 'ZTRAN', description='desc', package='$TMP',
            par_parent_transaction_code='SE38'
        )

        self._assert_common(transaction, 'ZTRAN', 'desc', '$TMP')
        self.assertEqual(transaction.definition.transaction_type, 'parameterTransaction')
        self.assertEqual(transaction.definition.parameter_transaction.par_parent_transaction_code, 'SE38')

    def test_dialog_transaction(self):
        conn = Connection()
        transaction = sap.adt.Transaction.dialog(
            conn, 'ZTRAN', description='desc', package='$TMP',
            program_name='SAPMTEST', program_dynnr='0100'
        )

        self._assert_common(transaction, 'ZTRAN', 'desc', '$TMP')
        self.assertEqual(transaction.definition.transaction_type, 'dialogTransaction')
        self.assertEqual(transaction.definition.dialog_transaction.program_name, 'SAPMTEST')
        self.assertEqual(transaction.definition.dialog_transaction.program_dynnr, '0100')

    def test_oo_transaction(self):
        conn = Connection()
        transaction = sap.adt.Transaction.oo(
            conn, 'ZTRAN', description='desc', package='$TMP',
            class_name='ZCL_TEST', method_name='EXECUTE'
        )

        self._assert_common(transaction, 'ZTRAN', 'desc', '$TMP')
        self.assertEqual(transaction.definition.transaction_type, 'ooTransaction')
        self.assertEqual(transaction.definition.oo_transaction.class_name, 'ZCL_TEST')
        self.assertEqual(transaction.definition.oo_transaction.method_name, 'EXECUTE')

    def test_oo_transaction_with_optional_fields(self):
        conn = Connection()
        transaction = sap.adt.Transaction.oo(
            conn, 'ZTRAN', description='desc', package='$TMP',
            class_name='ZCL_TEST', method_name='EXECUTE',
            oo_transaction_model=True, update_mode='synchronous',
            local_in_program=True, class_program_name='ZPROG'
        )

        self.assertTrue(transaction.definition.oo_transaction.oo_transaction_model)
        self.assertEqual(transaction.definition.update_mode, 'synchronous')
        self.assertTrue(transaction.definition.oo_transaction.local_in_program)
        self.assertEqual(transaction.definition.oo_transaction.class_program_name, 'ZPROG')

    def test_variant_transaction(self):
        conn = Connection()
        transaction = sap.adt.Transaction.variant(
            conn, 'ZTRAN', description='desc', package='$TMP',
            var_parent_transaction_code='MM01'
        )

        self._assert_common(transaction, 'ZTRAN', 'desc', '$TMP')
        self.assertEqual(transaction.definition.transaction_type, 'variantTransaction')
        self.assertEqual(transaction.definition.variant_transaction.var_parent_transaction_code, 'MM01')

    def test_variant_transaction_with_optional_fields(self):
        conn = Connection()
        transaction = sap.adt.Transaction.variant(
            conn, 'ZTRAN', description='desc', package='$TMP',
            var_parent_transaction_code='MM01',
            transaction_variant_cross_client=True,
            transaction_variant_name='ZVAR01'
        )

        self.assertTrue(transaction.definition.variant_transaction.transaction_variant_cross_client)
        self.assertEqual(transaction.definition.variant_transaction.transaction_variant_name, 'ZVAR01')

    def test_factory_passes_metadata(self):
        conn = Connection()
        metadata = sap.adt.ADTCoreData(description='test', language='EN', master_language='EN',
                                       responsible='DEV')
        transaction = sap.adt.Transaction.report(
            conn, 'ZTRAN', description='test', package='$TMP',
            metadata=metadata,
            report_name='ZREPORT', report_dynnr='1000'
        )

        self.assertEqual(transaction.master_language, 'EN')
        self.assertEqual(transaction.responsible, 'DEV')

    def test_factory_create_produces_correct_xml(self):
        conn = Connection()
        metadata = sap.adt.ADTCoreData(description='abapgit', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        transaction = sap.adt.Transaction.report(
            conn, TRANSACTION_NAME, description='abapgit', package='$TMP',
            metadata=metadata,
            report_name='ZABAPGIT', report_dynnr='1000'
        )

        transaction.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/aps/iam/tran',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.blues.v2+xml; charset=utf-8'},
            body=bytes(CREATE_TRANSACTION_WITH_CONTENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(conn.execs[0], self)


if __name__ == '__main__':
    unittest.main()
