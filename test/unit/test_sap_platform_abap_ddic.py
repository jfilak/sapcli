#!/usr/bin/env python3

import unittest

import sap.platform.abap.abapgit
from sap.platform.abap.ddic import VSEOCLASS, SEOSUBCOTX, DESCRIPTIONS_SUB

from fixtures_sap_platform_abap_ddic import CLAS_WITH_DESCRIPTIONS_SUB_XML


class TestDESCRIPTIONS_SUB(unittest.TestCase):

    def test_descriptions_sub_from_xml(self):
        parsed = sap.platform.abap.abapgit.from_xml([VSEOCLASS, DESCRIPTIONS_SUB],
                                                    CLAS_WITH_DESCRIPTIONS_SUB_XML)

        self.assertEqual(parsed['VSEOCLASS'].CLSNAME, 'ZCL_ABAPGIT_WHERE_USED_TOOLS')
        self.assertEqual(parsed['VSEOCLASS'].DESCRIPT, 'abapGit - Where-used Utilities')

        descriptions_sub = parsed['DESCRIPTIONS_SUB']
        self.assertEqual(len(descriptions_sub), 2)
        self.assertEqual(descriptions_sub[0], SEOSUBCOTX(CMPNAME='EXPAND_FUGR_TADIR_TO_FUNC',
                                                         SCONAME='ZCX_ABAPGIT_EXCEPTION',
                                                         LANGU='E',
                                                         DESCRIPT='abapGit - Exception'))
        self.assertEqual(descriptions_sub[1], SEOSUBCOTX(CMPNAME='SELECT_TADIR_ENTRIES',
                                                         SCONAME='IV_PACKAGE',
                                                         LANGU='E',
                                                         DESCRIPT='Package Name'))


if __name__ == '__main__':
    unittest.main()
