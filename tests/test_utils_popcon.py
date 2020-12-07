#!/usr/bin/env python3
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
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
import os
import requests
import requests_mock
import io

from DebianDevelChangesBot.utils import popcon


class TestPopcon(unittest.TestCase):
    def setUp(self):
        self.mocker = requests_mock.Mocker()
        self.mocker.start()

        self.session = requests.Session()

    def tearDown(self):
        self.mocker.stop()

    def _test(self, package="haskell-devscripts"):
        fixture = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "popcon", package
        )
        with open(fixture, encoding="utf-8") as f:
            data = f.read()

        self.mocker.register_uri("GET", "https://qa.debian.org/popcon.php", text=data)

        return popcon(package, self.session)

    def testRun(self):
        self.assertTrue(self._test())

    def testPackage(self):
        self.assertEqual(self._test().package, "haskell-devscripts")

    def testInst(self):
        self.assertEqual(self._test().inst, 96)

    def testVote(self):
        self.assertEqual(self._test().vote, 8)

    def testOld(self):
        self.assertEqual(self._test().old, 49)

    def testRecent(self):
        self.assertEqual(self._test().recent, 39)

    def testNofiles(self):
        self.assertEqual(self._test().nofiles, 0)


if __name__ == "__main__":
    unittest.main()
