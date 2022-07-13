#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

import sap
import sap.adt
import sap.adt.atc
import sap.adt.objects
from sap.adt.marshalling import Marshal

from mock import ConnectionViaHTTP as Connection, Response, Request
from fixtures_adt_atc import ADT_XML_ATC_CUSTOMIZING, ADT_XML_ATC_CUSTOMIZING_ATTRIBUTES, ADT_XML_ATC_RUN_REQUEST_CLASS, \
                             ADT_XML_ATC_RUN_RESPONSE_FAILURES, ADT_XML_ATC_RUN_RESPONSE_NO_OBJECTS, \
                             ADT_XML_ATC_WORKLIST_EMPTY, ADT_XML_ATC_WORKLIST_CLASS, ADT_XML_ATC_RUN_REQUEST_PACKAGE, \
                             ADT_XML_PROFILES_TABLE, ADT_XML_PROFILES_TRAN_TABLE, ADT_XML_PROFILES_CHECKS_TABLE, \
                             ADT_XML_PROFILES_CHKMSG_LOCAL_TABLE


HEADER_ACCEPT = f'application/xml, {sap.adt.atc.CUSTOMIZING_MIME_TYPE_V1}'
ATC_CUSTOMIZIN_REQUEST = Request('GET',
                                 '/sap/bc/adt/atc/customizing',
                                 headers={'Accept': HEADER_ACCEPT},
                                 body=None,
                                 params=None)


class TestCustomizing(unittest.TestCase):

    def test_fetch_response_customizing(self):
        conn = Connection([Response(status_code=200,
                                    content_type=sap.adt.atc.CUSTOMIZING_MIME_TYPE_V1,
                                    text=ADT_XML_ATC_CUSTOMIZING_ATTRIBUTES)])

        customizing = sap.adt.atc.fetch_customizing(conn)
        self.assertEqual(customizing.system_check_variant, 'OPENABAPCHECKS')

        self.assertEqual(conn.execs, [ATC_CUSTOMIZIN_REQUEST])

    def test_fetch_response_xml(self):
        conn = Connection([Response(status_code=200,
                                    content_type='application/xml',
                                    text=ADT_XML_ATC_CUSTOMIZING)])

        customizing = sap.adt.atc.fetch_customizing(conn)
        self.assertEqual(customizing.system_check_variant, 'STANDARD')

        self.assertEqual(conn.execs, [ATC_CUSTOMIZIN_REQUEST])


class TestRunRequest(unittest.TestCase):

    def test_run_request_serialization(self):
        conn = Connection()

        obj_sets = sap.adt.objects.ADTObjectSets()
        obj_sets.include_object(sap.adt.Class(conn, 'ZCL_Z001_DPC'))

        atc_run_req = sap.adt.atc.RunRequest(obj_sets, 100)
        atc_run_xml = Marshal().serialize(atc_run_req)

        self.maxDiff = None
        self.assertEqual(atc_run_xml, ADT_XML_ATC_RUN_REQUEST_CLASS)


class TestRunResponse(unittest.TestCase):

    def test_run_response_infos_empty(self):
        run_response = sap.adt.atc.RunResponse()
        sap.adt.marshalling.Marshal.deserialize(ADT_XML_ATC_RUN_RESPONSE_NO_OBJECTS, run_response)

        self.assertEqual(run_response.worklist_id, '0242AC1100021EE9AAE43D24739F1C3A')
        self.assertEqual(run_response.timestamp, '2019-07-20T19:09:34Z')

        self.assertEqual(len(run_response.infos), 1)

        info = run_response.infos[0]
        self.assertEqual(info.typ, 'NO_OBJS')
        self.assertEqual(info.description, 'Selection does not contain objects which can be checked by ATC')
        self.assertEqual(str(info), info.description)

    def test_run_response_infos_populated(self):
        run_response = sap.adt.atc.RunResponse()
        sap.adt.marshalling.Marshal.deserialize(ADT_XML_ATC_RUN_RESPONSE_FAILURES, run_response)

        self.assertEqual(run_response.worklist_id, '0242AC1100021EE9AAE43D24739F1C3A')
        self.assertEqual(run_response.timestamp, '2019-07-20T19:18:57Z')

        self.assertEqual(len(run_response.infos), 5)

        for i, info in enumerate(run_response.infos):
            if i == 4:
                self.assertEqual(info.typ, 'FINDING_STATS')
                self.assertEqual(info.description, '0,0,1')
            else:
                self.assertEqual(info.typ, 'TOOL_FAILURE')
                self.assertEqual(info.description, 'ATC check run aborted, due to missing prerequisites')


class TestWorkList(unittest.TestCase):

    def test_deserialize_empty(self):
        conn = Connection()

        worklist = sap.adt.atc.WorkList()
        sap.adt.marshalling.Marshal.deserialize(ADT_XML_ATC_WORKLIST_EMPTY, worklist)

        self.assertEqual(worklist.worklist_id, '0242AC1100021EE9AAE43D24739F1C3A')
        self.assertEqual(worklist.timestamp, '2019-07-20T19:09:34Z')
        self.assertEqual(worklist.used_objectset, '99999999999999999999999999999999')
        self.assertEqual(worklist.object_set_is_complete, 'true')

        self.assertEqual(len(worklist.object_sets), 1)

        object_set = worklist.object_sets[0]
        self.assertEqual(object_set.name, '00000000000000000000000000000000')
        self.assertEqual(object_set.title, 'All Objects')
        self.assertEqual(object_set.kind, 'ALL')

    def test_deserialize_populated(self):
        conn = Connection()

        worklist = sap.adt.atc.WorkList()
        sap.adt.marshalling.Marshal.deserialize(ADT_XML_ATC_WORKLIST_CLASS, worklist)

        self.assertEqual(worklist.worklist_id, '0242AC1100021EE9AAE43D24739F1C3A')
        self.assertEqual(worklist.timestamp, '2019-07-20T19:18:57Z')
        self.assertEqual(worklist.used_objectset, '99999999999999999999999999999999')
        self.assertEqual(worklist.object_set_is_complete, 'true')

        self.assertEqual(len(worklist.object_sets), 2)

        object_set = worklist.object_sets[0]
        self.assertEqual(object_set.name, '00000000000000000000000000000000')
        self.assertEqual(object_set.title, 'All Objects')
        self.assertEqual(object_set.kind, 'ALL')

        object_set = worklist.object_sets[1]
        self.assertEqual(object_set.name, '99999999999999999999999999999999')
        self.assertEqual(object_set.title, 'Last Check Run')
        self.assertEqual(object_set.kind, 'LAST_RUN')

        self.assertEqual(len(worklist.objects), 1)
        atcobject = worklist.objects[0]

        self.assertEqual(atcobject.uri, '/sap/bc/adt/atc/objects/R3TR/CLAS/ZCL_Z001_DPC')
        self.assertEqual(atcobject.typ, 'CLAS')
        self.assertEqual(atcobject.name, 'ZCL_Z001_DPC')
        self.assertEqual(atcobject.package_name, '$TMP')
        self.assertEqual(atcobject.author, 'DEVELOPER')
        self.assertEqual(atcobject.object_type_id, 'CLAS/OC')

        self.assertEqual(len(atcobject.findings), 1)
        finding = atcobject.findings[0]

        self.assertEqual(finding.uri, '/sap/bc/adt/atc/worklists/0242AC1100021EE9AAE43D24739F1C3A/findings/ZCL_Z001_DPC/CLAS/001321AF52A31DDBA7E0EE95D633EA22/0028/-1')
        self.assertEqual(finding.location, '/sap/bc/adt/oo/classes/zcl_z001_dpc#start=1,0')
        self.assertEqual(finding.priority, '3')
        self.assertEqual(finding.check_id, '001321AF52A31DDBA7E0EE95D633EA22')
        self.assertEqual(finding.check_title, 'Test Environment  (SLIN_UMFLD)')
        self.assertEqual(finding.message_id, '0028')
        self.assertEqual(finding.message_title, 'Inconsistency in the SAP configuration of time zones (0028)')
        self.assertEqual(finding.exemption_approval, '-')
        self.assertEqual(finding.exemption_kind, '')


class TestATCRunner(unittest.TestCase):

    def setUp(self):
        self.variant = 'ACT_VARIANT'
        self.worklist_id = 'WORKLIST_ID'

        self.request_create_worklist = Request(method='POST',
                                               adt_uri='/sap/bc/adt/atc/worklists',
                                               params={'checkVariant': self.variant},
                                               headers={'Accept': 'text/plain'},
                                               body=None)

        self.request_run_worklist = Request(method='POST',
                                            adt_uri='/sap/bc/adt/atc/runs',
                                            params={'worklistId': self.worklist_id},
                                            headers={'Accept': 'application/xml',
                                                     'Content-Type': 'application/xml'},
                                            body=ADT_XML_ATC_RUN_REQUEST_PACKAGE)

        self.request_get_worklist = Request(method='GET',
                                            adt_uri=f'/sap/bc/adt/atc/worklists/{self.worklist_id}',
                                            params={'includeExemptedFindings': 'false'},
                                            headers={'Accept': 'application/atc.worklist.v1+xml'},
                                            body=None)

        self.conn = Connection([Response(status_code=200,
                                         text=self.worklist_id,
                                         headers={'Content-Type': 'text/plain'}),
                                Response(status_code=200,
                                         text=ADT_XML_ATC_RUN_RESPONSE_NO_OBJECTS,
                                         headers={'Content-Type': 'application/xml'}),
                                Response(status_code=200,
                                         text=ADT_XML_ATC_WORKLIST_EMPTY,
                                         headers={'Content-Type': 'application/atc.worklist.v1+xml'})])

        self.checks_runner = sap.adt.atc.ChecksRunner(self.conn, self.variant)

    def test_get_id(self):
        worklist_id_1 = self.checks_runner._get_id()
        worklist_id_2 = self.checks_runner._get_id()

        self.assertEqual(self.worklist_id, worklist_id_1)
        self.assertEqual(worklist_id_1, worklist_id_2)

        self.assertEqual(self.conn.execs, [self.request_create_worklist])

    def test_run_for(self):
        objects = sap.adt.objects.ADTObjectSets()
        objects.include_object(sap.adt.Package(self.conn, '$iamtheking'))

        results = self.checks_runner.run_for(objects, max_verdicts=69)

        self.assertEqual(self.conn.execs, [self.request_create_worklist,
                                           self.request_run_worklist,
                                           self.request_get_worklist])

        self.assertIsNotNone(results.run_response)
        self.assertIsNotNone(results.worklist)


class TestATCProfiles(unittest.TestCase):

    def test_fetch_profiles(self):
        conn = Connection([Response(status_code=200,
                                    text=ADT_XML_PROFILES_TABLE)])

        profiles = sap.adt.atc.fetch_profiles(conn)

        self.assertEqual(profiles, {
            'PROFILE1': {
                'changed': '20080415161735',
                'changed_by': 'CHGUSER1',
                'created': '20010309180000',
                'created_by': 'CREUSER1'},
            'PROFILE2': {
                'changed': '00000000000000',
                'changed_by': '',
                'created': '20010328100000',
                'created_by': 'CREUSER2'}
            })

    def test_dump_profiles(self):
        conn = Connection([
            Response(status_code=200, text=ADT_XML_PROFILES_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_TRAN_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_CHECKS_TABLE)
        ])

        dump = sap.adt.atc.dump_profiles(conn)

        self.assertDictEqual(dump, {
            'profiles': {
                'PROFILE1': {
                    'changed': '20080415161735',
                    'changed_by': 'CHGUSER1',
                    'created': '20010309180000',
                    'created_by': 'CREUSER1',
                    'checks': {
                        'CHECK1_1': {
                            'sequence_number': '00000001',
                            'since': '00000091',
                            'note': 'Note PRF1 CHK1'
                        },
                        'CHECK1_2': {
                            'sequence_number': '00000002',
                            'since': '00000092',
                            'note': 'Note PRF1 CHK2'
                        }
                    },
                    'trans': {
                        'E': 'Standard Check Profile1 CheckMan 6.20'
                    }
                },
                'PROFILE2': {
                    'changed': '00000000000000',
                    'changed_by': '',
                    'created': '20010328100000',
                    'created_by': 'CREUSER2',
                    'checks': {
                        'CHECK2_1': {
                            'sequence_number': '00000003',
                            'since': '00000093',
                            'note': 'Note PRF2 CHK1'
                        }
                    },
                    'trans': {
                        'E': 'Standard Check Profile2 CheckMan 6.20'
                    }
                }
            }
        })

    def test_dump_profiles_filtered(self):
        conn = Connection([
            Response(status_code=200, text=ADT_XML_PROFILES_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_TRAN_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_CHECKS_TABLE)
        ])

        dump = sap.adt.atc.dump_profiles(conn, ['PROFILE1'])

        self.assertDictEqual(dump, {
            'profiles': {
                'PROFILE1': {
                    'changed': '20080415161735',
                    'changed_by': 'CHGUSER1',
                    'created': '20010309180000',
                    'created_by': 'CREUSER1',
                    'checks': {
                        'CHECK1_1': {
                            'sequence_number': '00000001',
                            'since': '00000091',
                            'note': 'Note PRF1 CHK1'
                        },
                        'CHECK1_2': {
                            'sequence_number': '00000002',
                            'since': '00000092',
                            'note': 'Note PRF1 CHK2'
                        }
                    },
                    'trans': {
                        'E': 'Standard Check Profile1 CheckMan 6.20'
                    }
                }
            }
        })

    def test_dump_profiles_filtered_with_checkman(self):
        conn = Connection([
            Response(status_code=200, text=ADT_XML_PROFILES_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_TRAN_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_CHECKS_TABLE),
            Response(status_code=200, text=ADT_XML_PROFILES_CHKMSG_LOCAL_TABLE)
        ])

        self.maxDiff = None

        dump = sap.adt.atc.dump_profiles(conn, ['PROFILE1'], True)

        self.assertDictEqual(dump, {
            'profiles': {
                'PROFILE1': {
                    'changed': '20080415161735',
                    'changed_by': 'CHGUSER1',
                    'created': '20010309180000',
                    'created_by': 'CREUSER1',
                    'checks': {
                        'CHECK1_1': {
                            'sequence_number': '00000001',
                            'since': '00000091',
                            'note': 'Note PRF1 CHK1'
                        },
                        'CHECK1_2': {
                            'sequence_number': '00000002',
                            'since': '00000092',
                            'note': 'Note PRF1 CHK2'
                        }
                    },
                    'trans': {
                        'E': 'Standard Check Profile1 CheckMan 6.20'
                    }
                }
            },
            'checkman_messages_local': [
                {
                    'check_id': 'CHECK1_1',
                    'check_message_id': '0001',
                    'check_view': '',
                    'deactivated': '',
                    'local_prio': '2',
                    'valid_id': '',
                    'valid_to': '20250802'
                },
                {
                    'check_id': 'CHECK1_2',
                    'check_message_id': 'EHPW',
                    'check_view': '',
                    'deactivated': 'X',
                    'local_prio': '4',
                    'valid_id': 'Requested by Bob and Alice',
                    'valid_to': '20250802'
                }
            ]
        })


if __name__ == '__main__':
    unittest.main(verbosity=100)
