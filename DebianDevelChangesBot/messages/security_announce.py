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

from DebianDevelChangesBot import Message


class SecurityAnnounceMessage(Message):
    FIELDS = ("dsa_number", "dsa_revision", "package", "problem", "year")

    def format(self):
        msg = "[security]Security[reset] [version]DSA-%d-%d[reset] - " % (
            self.dsa_number,
            self.dsa_revision,
        )

        msg += "New %s packages %s. " % (self.package_name(), self.problem)

        msg += "[url]https://www.debian.org/security/%s/dsa-%d[/url]" % (
            self.year,
            self.dsa_number,
        )

        return msg
