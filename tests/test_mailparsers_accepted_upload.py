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

from glob import glob
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DebianDevelChangesBot.utils import parse_mail
from DebianDevelChangesBot.mailparsers import AcceptedUploadParser as p


class TestMailParserAcceptedUpload(unittest.TestCase):
    def setUp(self):
        self.headers = {"List-Id": "<debian-devel-changes.lists.debian.org>"}

        self.body = [
            "-----BEGIN PGP SIGNED MESSAGE-----",
            "Hash: SHA1",
            "",
            "Format: 1.7",
            "Date: Thu, 03 Apr 2008 11:45:26 +0100",
            "Source: haskell-irc",
            "Binary: libghc6-irc-dev libghc6-irc-doc",
            "Architecture: source i386 all",
            "Version: 0.4.2-1",
            "Distribution: unstable",
            "Urgency: low",
            "Maintainer: Chris Lamb <maint@t.com>",
            "Changed-By: Chris Lamb <change@t.com>",
            "Description: ",
            " libghc6-irc-dev - GHC 6 libraries for the Haskell IRC library",
            " libghc6-irc-doc - GHC 6 libraries for the Haskell IRC library (documentation)",
            "Changes: ",
            # etc.
        ]

    def testSimple(self):
        msg = p.parse(self.headers, self.body)

        self.assertTrue(msg)
        self.assertEqual(msg.package, "haskell-irc")
        self.assertEqual(msg.version, "0.4.2-1")
        self.assertEqual(msg.distribution, "unstable")
        self.assertEqual(msg.urgency, "low")
        self.assertEqual(msg.by, "Chris Lamb <change@t.com>")
        self.assertEqual(msg.closes, None)

    def testCloses(self):
        self.body.append("Closes: 123456 456123")
        msg = p.parse(self.headers, self.body)

        self.assertTrue(msg)
        self.assertEqual(msg.closes, [123456, 456123])

    def testQuotedPrintableChangedBy(self):
        self.body[12] = "Changed-By: Gon=C3=A9ri Le Bouder <a@b.com>"

        msg = p.parse(self.headers, self.body)
        self.assertTrue(msg)
        self.assertEqual(msg.by, "Gonéri Le Bouder <a@b.com>")

    def testUrgencyCase(self):
        self.body[10] = "Urgency: HIGH"

        msg = p.parse(self.headers, self.body)
        self.assertTrue(msg)
        self.assertEqual(msg.urgency, "high")

    def testFixtures(self):
        dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "accepted_upload",
            "*",
        )
        for filename in glob(dir):
            with open(filename, "rb") as f:
                mail = parse_mail(f)
            msg = p.parse(*mail)
            self.assertTrue(msg)


if __name__ == "__main__":
    unittest.main()
