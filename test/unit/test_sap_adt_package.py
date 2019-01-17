#!/bin/python

import unittest

import sap.adt

from mock import Connection

FIXTURE_PACKAGE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<pak:package xmlns:pak="http://www.sap.com/adt/packages" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:version="active" adtcore:type="DEVC/K" adtcore:description="description" adtcore:name="$TEST">
<pak:applicationComponent/>
<pak:attributes pak:packageType="development"/>
<pak:packageInterfaces/>
<adtcore:packageRef adtcore:name="$TEST"/>
<pak:subPackages/>
<pak:superPackage/>
<pak:translation/>
<pak:transport>
<pak:softwareComponent pak:name="LOCAL"/>
<pak:transportLayer/>
</pak:transport>
<pak:useAccesses/>
</pak:package>"""

class TestADTPackage(unittest.TestCase):

    def test_init(self):
        conn = Connection()

        package = sap.adt.Package(conn, '$TEST')
        package.description = 'description'
        package.set_package_type('development')
        package.set_software_component('LOCAL')
        package.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], 'packages')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.packages.v1+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_PACKAGE_XML)


if __name__ == '__main__':
    unittest.main()
