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

import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot.utils import tidy_bug_title


class TestFormatEmail(unittest.TestCase):
    def _test(self, title, package, ret):
        self.assertEqual(tidy_bug_title(title, package), ret)

    def testMatch(self):
        self._test("[a]: b", "a", "b")

    def testCaseMatch(self):
        self._test("[A]: b", "a", "b")

    def testCaseMatch2(self):
        self._test("[a]: b", "A", "b")

    def testNoMatch(self):
        self._test("[a]: b", "c", "[a]: b")

    def testNoBraceMatch(self):
        self._test("a: b", "a", "b")

    def testNoBraceNoMatch(self):
        self._test("a: b", "c", "a: b")

    def testNoColonMatch(self):
        self._test("[a] b", "a", "b")

    def testNoColonNoMatch(self):
        self._test("[a] b", "c", "[a] b")

    def testRemoveDoubleSpace(self):
        self._test("a  b", "packagename", "a b")

    def testRepeatedSubject(self):
        self._test("Subject: a", "packagename", "a")


if __name__ == "__main__":
    unittest.main()
