#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb

from mock import Connection, Response, Request

from fixtures_sap_adt_metadatextension import (
    METADATA_EXTENSION_NAME,
    METADATA_EXTENSION_ADT_GET_EXISTING_RESPONSE_XML,
    METADATA_EXTENSION_ADT_NEW_OBJECT_REQUEST_XML,
    METADATA_EXTENSION_ADT_GET_ACTIVE_RESPONSE_XML,
    METADATA_EXTENSION_CODE,
)


FIXTURE_ACTIVATION_REQUEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/ddlx/sources/z_test_md_ext_v0" adtcore:name="Z_TEST_MD_EXT_V0"/>
</adtcore:objectReferences>'''


class TestADTMetadataExtension(unittest.TestCase):

    def test_adt_ddlx_init(self):
        metadata = sap.adt.ADTCoreData()

        ddlx = sap.adt.MetadataExtension('CONNECTION', name=METADATA_EXTENSION_NAME,
                                         package='PACKAGE', metadata=metadata)
        self.assertEqual(ddlx.name, METADATA_EXTENSION_NAME)
        self.assertEqual(ddlx.reference.name, 'PACKAGE')
        self.assertEqual(ddlx.coredata, metadata)

    def test_adt_ddlx_objtype(self):
        ddlx = sap.adt.MetadataExtension('CONNECTION', name=METADATA_EXTENSION_NAME)
        self.assertEqual(ddlx.objtype.code, 'DDLX/EX')
        self.assertEqual(ddlx.objtype.basepath, 'ddic/ddlx/sources')
        self.assertEqual(ddlx.objtype.mimetype, 'application/vnd.sap.adt.ddic.ddlx.v1+xml')
        self.assertEqual(ddlx.objtype.xmlname, 'ddlxSource')

    def test_adt_ddlx_uri(self):
        ddlx = sap.adt.MetadataExtension('CONNECTION', name=METADATA_EXTENSION_NAME)
        self.assertEqual(ddlx.uri, 'ddic/ddlx/sources/z_test_md_ext_v0')

    def test_adt_ddlx_fetch(self):
        conn = Connection([Response(text=METADATA_EXTENSION_ADT_GET_EXISTING_RESPONSE_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.ddic.ddlx.v1+xml; charset=utf-8'})])

        ddlx = sap.adt.MetadataExtension(conn, name=METADATA_EXTENSION_NAME)
        ddlx.fetch()

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/ddic/ddlx/sources/z_test_md_ext_v0')])

        self.assertEqual(ddlx.name, METADATA_EXTENSION_NAME)
        self.assertEqual(ddlx.description, 'dfadfa')
        self.assertEqual(ddlx.reference.name, '$TMP')
        self.assertEqual(ddlx.master_language, 'EN')

    def test_adt_ddlx_read(self):
        conn = Connection([Response(text=METADATA_EXTENSION_CODE,
                                    status_code=200,
                                    headers={'Content-Type': 'text/plain; charset=utf-8'})])

        ddlx = sap.adt.MetadataExtension(conn, name=METADATA_EXTENSION_NAME)
        code = ddlx.text

        self.assertEqual(conn.mock_methods(),
                         [('GET', '/sap/bc/adt/ddic/ddlx/sources/z_test_md_ext_v0/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, METADATA_EXTENSION_CODE)

    def test_adt_ddlx_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(description='dfadfa', language='EN', master_language='EN',
                                       master_system='C50', responsible='DEVELOPER')
        ddlx = sap.adt.MetadataExtension(conn, METADATA_EXTENSION_NAME, package='$TMP', metadata=metadata)
        ddlx.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/ddic/ddlx/sources',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.ddic.ddlx.v1+xml; charset=utf-8'},
            body=bytes(METADATA_EXTENSION_ADT_NEW_OBJECT_REQUEST_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(conn.execs[0], self)

    def test_adt_ddlx_activate(self):
        conn = Connection([
            Response(text='', status_code=200, headers={}),
            Response(text=METADATA_EXTENSION_ADT_GET_ACTIVE_RESPONSE_XML,
                     status_code=200,
                     headers={'Content-Type': 'application/xml; charset=utf-8'})
        ])

        ddlx = sap.adt.MetadataExtension(conn, name=METADATA_EXTENSION_NAME)
        sap.adt.wb.activate(ddlx)

        self.assertEqual(conn.mock_methods(), [
            ('POST', '/sap/bc/adt/activation'),
            ('GET', '/sap/bc/adt/ddic/ddlx/sources/z_test_md_ext_v0')
        ])

        get_request = conn.execs[0]
        self.assertEqual(get_request.body, FIXTURE_ACTIVATION_REQUEST_XML)


if __name__ == '__main__':
    unittest.main()
