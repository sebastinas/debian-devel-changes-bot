#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
#   Copyright (C) 2016 Sebastian Ramacher <sramacher@debian.org>
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

from __future__ import unicode_literals
import io
import unittest
import requests
import requests_mock

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot.datasources import Dinstall


class TestDatasourceDinstall(unittest.TestCase):
    def setUp(self):
        fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'fixtures', 'dinstall.status.done')
        with io.open(fixture, encoding='utf-8') as f:
            self.data_not_running = f.read()

        fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'fixtures', 'dinstall.status.running')
        with io.open(fixture, encoding='utf-8') as f:
            self.data_running = f.read()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()

        session = requests.Session()
        self.datasource = Dinstall(session)

    def tearDown(self):
        self.mocker.stop()

    def testNotRunning(self):
        self.mocker.register_uri('GET', Dinstall.URL,
                                 text=self.data_not_running)
        self.datasource.update()
        self.assertEqual(self.datasource.get_status(), 'not running')

    def testRunning(self):
        self.mocker.register_uri('GET', Dinstall.URL, text=self.data_running)
        self.datasource.update()
        self.assertEqual(self.datasource.get_status(), 'running')


if __name__ == "__main__":
    unittest.main()
