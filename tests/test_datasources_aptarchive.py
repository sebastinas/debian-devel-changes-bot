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

import unittest
import tempfile
import shutil

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot.datasources import AptArchive


class TestDatasourceAptArchive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # FIXME make sure we do not have to fetch
        apt_config = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'bot-config', 'apt')
        cls.statedir = tempfile.mkdtemp()

        cls.apt_archive = AptArchive(apt_config, cls.statedir)
        cls.apt_archive.update_index(True)
        cls.apt_archive.update()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.statedir, True)

    def testVLC(self):
        info = self.apt_archive.get_maintainer('vlc')
        self.assertEqual(info['email'], 'pkg-multimedia-maintainers@lists.alioth.debian.org')
        self.assertEqual(info['name'], 'Debian Multimedia Maintainers')

    def testSourceVLC(self):
        info = self.apt_archive.get_maintainer('src:vlc')
        self.assertEqual(info['email'], 'pkg-multimedia-maintainers@lists.alioth.debian.org')
        self.assertEqual(info['name'], 'Debian Multimedia Maintainers')

    def testUdev(self):
        info = self.apt_archive.get_maintainer('udev')
        self.assertEqual(info['email'], 'pkg-systemd-maintainers@lists.alioth.debian.org')
        self.assertEqual(info['name'], 'Debian systemd Maintainers')

    def testPseudoPackage(self):
        info = self.apt_archive.get_maintainer('wnpp')
        self.assertEqual(info['email'], 'wnpp@debian.org')


if __name__ == "__main__":
    unittest.main()
