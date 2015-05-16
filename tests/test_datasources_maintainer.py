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
import unittest

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot import Datasource
from DebianDevelChangesBot.datasources import Maintainer

class TestDatasourceMaintainer(unittest.TestCase):

    def setUp(self):
        self.fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)), \
            'fixtures', 'qa_page.html')

        self.datasource = Maintainer()

    def testInfo(self):
        with open(self.fixture) as fileobj:
            info = self.datasource.get_maintainer('vlc', fileobj=fileobj)
        self.assertEqual(info['email'], 'pkg-multimedia-maintainers@lists.alioth.debian.org')
        self.assertEqual(info['name'], 'Debian Multimedia Maintainers')

if __name__ == "__main__":
    unittest.main()
