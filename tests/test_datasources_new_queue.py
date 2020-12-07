#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2015 Sebastian Ramacher <sramacher@debian.org>
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

from DebianDevelChangesBot.datasources import NewQueue


class TestDatasourceTestingNewQueue(unittest.TestCase):
    def setUp(self):
        fixture = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "new_queue.txt"
        )
        with open(fixture, encoding="utf-8") as f:
            data = f.read()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.mocker.register_uri("GET", NewQueue.URL, text=data)

        session = requests.Session()
        self.datasource = NewQueue(session)

    def tearDown(self):
        self.mocker.stop()

    def is_new(self, package, version):
        self.datasource.update()
        return self.datasource.is_new(package, version)

    def testURL(self):
        """
        Check we have a sane URL.
        """
        self.assertTrue(len(self.datasource.URL) > 5)
        self.assertTrue(self.datasource.URL.startswith("http"))

    def testInterval(self):
        """
        Check we have a sane update interval.
        """
        self.assertTrue(self.datasource.INTERVAL > 60)

    def testTop(self):
        self.assertTrue(self.is_new("ezmlm-idx", "6.0.1-1"))

    def testBottom(self):
        self.assertTrue(self.is_new("libxml-sax-expatxs-perl", "1.31-1"))

    def testMultipleVersions(self):
        self.assertTrue(self.is_new("libgcal", "0.8.1-1"))
        self.assertTrue(self.is_new("libgcal", "0.8.1-2"))

    def testInvalidVersion(self):
        self.assertFalse(self.is_new("rcpp", "0.5.2.invalid"))

    def testNotInQueue(self):
        self.assertFalse(self.is_new("package-not-in-new-queue", "version-foo"))

    def testByhand(self):
        self.assertFalse(self.is_new("loadlin", "1.6c.really1.6c.nobin-2"))

    def testExperimental(self):
        self.assertTrue(self.is_new("ooo-build", "3.0.0.9+r14588-1"))


if __name__ == "__main__":
    unittest.main()
