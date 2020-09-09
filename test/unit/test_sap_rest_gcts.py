#!/usr/bin/env python3

import unittest

import sap.rest.gcts


class TestgCTSUtils(unittest.TestCase):

    def test_parse_url_https_git(self):
        package = sap.rest.gcts.package_name_from_url('https://example.org/foo/community.sap.git')
        self.assertEqual(package, 'community.sap')

    def test_parse_url_https(self):
        package = sap.rest.gcts.package_name_from_url('https://example.org/foo/git.no.suffix')
        self.assertEqual(package, 'git.no.suffix')
