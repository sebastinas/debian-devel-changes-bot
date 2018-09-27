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

from DebianDevelChangesBot.mailparsers import BugSubmittedParser as p


class TestMailParserBugSubmitted(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "Subject": "Bug#123456: Bug title",
            "From": "Submitter Name <name@t.com>",
            "List-Id": "<debian-bugs-dist.lists.debian.org>",
            "X-Debian-PR-Message": "report 654321",
            "X-Debian-PR-Package": "package-name",
        }

        self.body = [
            "Package: package-name",
            "Version: version-here",
            "",
            "Description",
        ]

    def testSimple(self):
        msg = p.parse(self.headers, self.body)

        self.assertTrue(msg)
        self.assertEqual(msg.package, "package-name")
        self.assertEqual(msg.version, "version-here")
        self.assertEqual(msg.by, "Submitter Name <name@t.com>")

    def testVersionWithSpaces(self):
        self.body[1] = "Version: version with spaces"
        msg = p.parse(self.headers, self.body)

        self.assertFalse(msg.version)

    def testAlternateEmailFormatting(self):
        self.headers["From"] = "name@t.com (Submitter Name)"

        msg = p.parse(self.headers, self.body)
        self.assertTrue(msg)
        self.assertEqual(msg.by, "Submitter Name <name@t.com>")


if __name__ == "__main__":
    unittest.main()
