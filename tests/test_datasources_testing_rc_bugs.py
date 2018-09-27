#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import requests
import requests_mock

from DebianDevelChangesBot.datasources import TestingRCBugs, StableRCBugs


class BaseTest(object):
    def setUp(self):
        fixture = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures',
            'testing_rc_bugs.json',
        )
        with open(fixture) as f:
            data = f.read()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.mocker.register_uri('GET', self.klass.URL, text=data)

        session = requests.Session()
        self.datasource = self.klass(session)

    def tearDown(self):
        self.mocker.stop()

    def testURL(self):
        """
        Check we have a sane URL.
        """
        self.assertTrue(len(self.datasource.URL) > 5)
        self.assertTrue(self.datasource.URL.startswith('https'))
        self.assertTrue('udd.debian.org' in self.datasource.URL)

    def testInterval(self):
        """
        Check we have a sane update interval.
        """
        self.assertTrue(self.datasource.INTERVAL > 60)

    def testParse(self):
        self.datasource.update()
        val = self.datasource.get_bugs()

        self.assertTrue(type(val) is set)
        self.assertEqual(len(val), 66)


class TestDatasourceTestingRCBugs(BaseTest, unittest.TestCase):
    klass = TestingRCBugs


class TestDatasourceStableRCBugs(BaseTest, unittest.TestCase):
    klass = StableRCBugs


if __name__ == "__main__":
    unittest.main()
