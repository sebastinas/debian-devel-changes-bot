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

from __future__ import unicode_literals
import io
import unittest
import requests
import requests_mock

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot.datasources import Maintainer


class TestDatasourceMaintainer(unittest.TestCase):
    def setUp(self):
        fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'fixtures', 'qa_page.html')
        with io.open(fixture, encoding='utf-8') as f:
            data = f.read()

        self.mocker = requests_mock.Mocker()
        self.mocker.start()
        self.mocker.register_uri('GET', Maintainer.get_pool_url('vlc'), text=data)

        session = requests.Session()
        self.datasource = Maintainer(session)


    def tearDown(self):
        self.mocker.stop()


    def testInfo(self):
        info = self.datasource.get_maintainer('vlc')
        self.assertEqual(info['email'], 'pkg-multimedia-maintainers@lists.alioth.debian.org')
        self.assertEqual(info['name'], 'Debian Multimedia Maintainers')


if __name__ == "__main__":
    unittest.main()
