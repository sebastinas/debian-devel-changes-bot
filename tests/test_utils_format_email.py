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

from DebianDevelChangesBot.utils import format_email_address

class TestFormatEmail(unittest.TestCase):
    def _test(self, val, ret):
        self.assertEqual(format_email_address(val, max_user=100, max_domain=100), ret)

    def testDebian(self):
        self._test("John Smith <jsmith@debian.org>", "John Smith (jsmith)")

    def testDebianDoubleQuotes(self):
        self._test('"John Smith" <jsmith@debian.org>', "John Smith (jsmith)")

    def testDebianSingleQuotes(self):
        self._test("'John Smith' <jsmith@debian.org>", "John Smith (jsmith)")

    def testSingleQuotesInName(self):
        self._test("John S'mith <jsmith@debian.org>", "John S'mith (jsmith)")

    def testNonNormalDebianEmailOne(self):
        self._test('John Smith <jsmith@merkel.debian.org>', 'John Smith (jsmith)')

    def testNonNormalDebianEmailTwo(self):
        self._test('John Smith <jsmith@master.debian.org>', 'John Smith (jsmith)')

    def testUppercaseDebianEmail(self):
        self._test('John Smith <JSMITH@DEBIAN.ORG>', "John Smith (jsmith)")

    def testUppercaseEmail(self):
        self._test('John Smith <JSMITH@HOST.TLD>', "John Smith <jsmith@host.tld>")

    def testExtraSpacesOne(self):
        self._test("John  Smith <jsmith@host.tld>", "John Smith <jsmith@host.tld>")

    def testExtraSpacesTwo(self):
        self._test("John Smith  <jsmith@host.tld>", "John Smith <jsmith@host.tld>")

    def testExtraSpacesThree(self):
        self._test("John Smith < jsmith@host.tld>", "John Smith <jsmith@host.tld>")

    def testExtraSpacesFour(self):
        self._test("John Smith < jsmith@host.tld>", "John Smith <jsmith@host.tld>")

    def testDontRepeatName(self):
        self._test("John Smith (jsmith) <jsmith@debian.org>", "John Smith (jsmith)")

    def testDontRepeatNameUppercase(self):
        self._test("John Smith (JSMITH) <jsmith@debian.org>", "John Smith (jsmith)")

    def testNoName(self):
        self._test("jsmith@debian.org", "jsmith@debian.org")

    def testNoNameTwo(self):
        self._test("<jsmith@debian.org>", "(jsmith)")

    def testRepeatEmailAddress(self):
        self._test('"leo@dicea.unifi.it" <leo@dicea.unifi.it>', '<leo@dicea.unifi.it>')

    def testReversedBracketed(self):
        self._test("<jsmith@host.tld> (John Smith)", "John Smith <jsmith@host.tld>")

    def testReverseDebianBracketed(self):
        self._test("<jsmith@debian.org> (John Smith)", "John Smith (jsmith)")

    def testReversed(self):
        self._test("jsmith@host.tld (John Smith)", "John Smith <jsmith@host.tld>")

    def testReverseDebian(self):
        self._test("jsmith@debian.org (John Smith)", "John Smith (jsmith)")

    def testReverseDebianUtf(self):
        self._test("jredrejo@debian.org (José L. Redrejo Rodríguez)", "José L. Redrejo Rodríguez (jredrejo)")

class TestLongEmail(unittest.TestCase):
    def _test(self, val, ret, max_user, max_domain):
        self.assertEqual(format_email_address(val, max_user=max_user,
            max_domain=max_domain), ret)

    def testZeroZero(self):
        self._test("E <1234567890@123456789>", "E <...@...>", 0, 0)

    def testOneUser(self):
        for i in range(1, 10):
            self._test("E <1@123456789>", "E <1@...>", i, 0)

    def testOneHost(self):
        for i in range(1, 10):
            self._test("E <123456789@1>", "E <...@1>", 0, i)

    def testPartTruncatedUser(self):
        self._test("E <123456789@123456789>", "E <12...@...>", 5, 0)

    def testPartTruncatedHost(self):
        self._test("E <123456789@123456789>", "E <...@12...>", 0, 5)

    def testBorderlineNotTruncatedUser(self):
        self._test("E <123456789@123456789>", "E <123456789@...>", 9, 0)

    def testBorderlineNotTruncatedHost(self):
        self._test("E <123456789@123456789>", "E <...@123456789>", 0, 9)

    def testBorderlineTruncatedUser(self):
        self._test("E <123456789@123456789>", "E <12345...@...>", 8, 0)

    def testBorderlineTruncatedHost(self):
        self._test("E <123456789@123456789>", "E <...@12345...>", 0, 8)

    def testNoExtraDotsAtEndUser(self):
        self._test("E <foo..bar@123456789>", "E <foo...@...>", 6, 0)
        self._test("E <foo..bar@123456789>", "E <foo...@...>", 7, 0)

    def testNoExtraDotsAtEndHost(self):
        self._test("E <123456789@foo..com>", "E <...@foo...>", 0, 7)
        self._test("E <123456789@foo..com>", "E <...@foo...>", 0, 6)

if __name__ == "__main__":
    unittest.main()
