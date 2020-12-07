#!/usr/bin/env python3
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

from DebianDevelChangesBot.utils.decoding import split_address


class TestUtilsDecoding(unittest.TestCase):
    def testSplitAddress1(self):
        addr = split_address("Sebastian Ramacher <sramacher@debian.org>")
        self.assertEqual(addr["name"], "Sebastian Ramacher")
        self.assertEqual(addr["email"], "sramacher@debian.org")

    def testSplitAddress2(self):
        addr = split_address("sramacher@debian.org")
        self.assertEqual(addr["name"], "")
        self.assertEqual(addr["email"], "sramacher@debian.org")


if __name__ == "__main__":
    unittest.main()
