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
import io

from DebianDevelChangesBot.datasources import RmQueue


class TestDatasourceTestingRmQueue(unittest.TestCase):
    def setUp(self):
        fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'fixtures', 'rm_queue.html')
        with io.open(fixture, encoding='utf-8') as f:
            data = f.read()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.mocker.register_uri('GET', RmQueue.URL, text=data)

        session = requests.Session()
        self.datasource = RmQueue(session)

    def tearDown(self):
        self.mocker.stop()

    def testURL(self):
        """
        Check we have a sane URL.
        """
        self.assertTrue(len(self.datasource.URL) > 5)
        self.assertTrue(self.datasource.URL.startswith('http'))

    def testInterval(self):
        """
        Check we have a sane update interval.
        """
        self.assertTrue(self.datasource.INTERVAL > 60)

    def testSize(self):
        self.datasource.update()
        self.assertEqual(self.datasource.get_size(), 5)

    def testTop(self):
        self.datasource.update()
        self.assertTrue(self.datasource.is_rm('mtasc'))

    def testBottom(self):
        self.datasource.update()
        self.assertTrue(self.datasource.is_rm('rnahybrid'))


if __name__ == "__main__":
    unittest.main()
