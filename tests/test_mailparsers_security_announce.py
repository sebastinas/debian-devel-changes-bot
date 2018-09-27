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

from DebianDevelChangesBot.mailparsers import SecurityAnnounceParser as p
from DebianDevelChangesBot.utils import parse_mail


def parse(number):
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fixtures",
        "security_announce",
        "%d.txt" % number,
    )
    with open(filename, "rb") as infile:
        mail = parse_mail(infile)
        msg = p.parse(*mail)
        assert msg
        return msg.__dict__


class TestMailParserSecurityAnnounce(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "List-Id": "<debian-security-announce.lists.debian.org>",
            "Date": "Sat, 19 Apr 2008 19:18:38 +0100",
            "Subject": "[SECURITY] [DSA 1234-5] New pinafore packages "
            "fix inertial dampener problem",
        }

    def testSimple(self):
        msg = p.parse(self.headers, [])

        self.assertTrue(msg)
        self.assertEqual(msg.dsa_number, 1234)
        self.assertEqual(msg.dsa_revision, 5)
        self.assertEqual(msg.package, "pinafore")
        self.assertEqual(msg.problem, "fix inertial dampener problem")
        self.assertEqual(msg.year, 2008)

    def testNoDate(self):
        del self.headers["Date"]
        self.assertFalse(p.parse(self.headers, []))

    def testNoSubject(self):
        del self.headers["Subject"]
        self.assertFalse(p.parse(self.headers, []))

    def testNoListId(self):
        del self.headers["List-Id"]
        self.assertFalse(p.parse(self.headers, []))

    def testWrongListId(self):
        self.headers["List-Id"] = "<debian-ponies-announce.lists.debian.org>"
        self.assertFalse(p.parse(self.headers, []))

    def test1(self):
        self.assertEqual(
            parse(1),
            {
                "dsa_revision": 1,
                "problem": "fix cross-site request forgery",
                "year": 2008,
                "dsa_number": 1553,
                "package": "ikiwiki",
            },
        )

    def subject_variation(self, subject):
        self.headers["Subject"] = "[SECURITY] [DSA 1234-5] %s" % subject
        data = p.parse(self.headers, [])
        self.assertEqual(data.package, "foo")
        self.assertEqual(data.problem, "fix bar problem")

    def testSubjectVariationNoNew(self):
        self.subject_variation("foo packages fix bar problem")

    def testSubjectVariationCapitalNew(self):
        self.subject_variation("New foo packages fix bar problem")

    def testSubjectVariationLowerNew(self):
        self.subject_variation("new foo packages fix bar problem")


if __name__ == "__main__":
    unittest.main()
