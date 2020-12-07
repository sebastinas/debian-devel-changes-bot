#!/usr/bin/env python3
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2018 Sebastian Ramacher <sramacher@debian.org>
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

from DebianDevelChangesBot.utils import rewrite_topic


class TestRewriteTopic(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(rewrite_topic("", "", 0), "")

    def testSimple(self):
        self.assertEqual(
            rewrite_topic("RC bug count: 1", "RC bug count", 2), "RC bug count: 2"
        )

    def testEmbedded(self):
        self.assertEqual(
            rewrite_topic("pre | RC bug count: 1 | post", "RC bug count", 2),
            "pre | RC bug count: 2 | post",
        )

    def testEmbedded2(self):
        self.assertEqual(
            rewrite_topic(
                "pre | RC bug count: 1 | Stable RC bug count: 3 | post",
                "RC bug count",
                2,
            ),
            "pre | RC bug count: 2 | Stable RC bug count: 3 | post",
        )


if __name__ == "__main__":
    unittest.main()
