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

from DebianDevelChangesBot import MailParser
from DebianDevelChangesBot.messages import SecurityAnnounceMessage

import re


SUBJECT = re.compile(
    r"^\[SECURITY\] \[DSA[-\s]([\d]+)-([\d+])\] (?:[Nn]ew )?(.+) package?s? (.*)$"
)
DATE = re.compile(r"(20\d\d)")


class SecurityAnnounceParser(MailParser):
    @staticmethod
    def parse(headers, body, **kwargs):
        if headers.get("List-Id", "") != "<debian-security-announce.lists.debian.org>":
            return

        msg = SecurityAnnounceMessage()

        m = SUBJECT.match(headers.get("Subject", ""))
        if m:
            try:
                msg.dsa_number = int(m.group(1))
                msg.dsa_revision = int(m.group(2))
            except ValueError:
                return

            msg.package = m.group(3)
            msg.problem = m.group(4)

        m = DATE.search(headers.get("Date", ""))
        if m:
            try:
                msg.year = int(m.group(1))
            except ValueError:
                return

        return msg
