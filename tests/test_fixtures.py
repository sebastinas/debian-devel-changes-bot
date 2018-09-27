#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from glob import glob

from DebianDevelChangesBot.messages import (
    AcceptedUploadMessage,
    BugClosedMessage,
    BugSubmittedMessage,
    SecurityAnnounceMessage,
)
from DebianDevelChangesBot.mailparsers import (
    AcceptedUploadParser,
    BugClosedParser,
    BugSubmittedParser,
    SecurityAnnounceParser,
)
from DebianDevelChangesBot.utils import parse_mail, colourise


class TestFixtures(unittest.TestCase):
    count = 0


def add_tests(testdir, parser, expected_type, test=lambda x: bool(x)):
    testdir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures", testdir, "*"
    )

    for filename in glob(testdir):

        def testFunc(self, filename=filename):
            with open(filename, "rb") as infile:
                try:
                    headers, body = parse_mail(infile)
                    msg = parser.parse(headers, body)
                except Exception:
                    print("Exception when parsing %s" % filename)
                    raise

            self.assertTrue(
                isinstance(msg, expected_type),
                "%s did not match with its parser: expected %s, got %s"
                % (filename, expected_type, type(msg)),
            )
            self.assertTrue(test(msg), "%s did not pass test" % filename)

            if msg:
                txt = msg.format()
                txt = colourise(txt)

        TestFixtures.count += 1
        setattr(TestFixtures, "test%d" % TestFixtures.count, testFunc)


add_tests("accepted_upload", AcceptedUploadParser, AcceptedUploadMessage)
add_tests("bug_closed", BugClosedParser, BugClosedMessage)
add_tests("bug_submitted", BugSubmittedParser, BugSubmittedMessage)
add_tests("security_announce", SecurityAnnounceParser, SecurityAnnounceMessage)

for parser in (
    AcceptedUploadParser,
    BugClosedParser,
    BugSubmittedParser,
    SecurityAnnounceParser,
):
    add_tests("non_messages", parser, type(None), test=lambda x: not bool(x))

if __name__ == "__main__":
    unittest.main()
