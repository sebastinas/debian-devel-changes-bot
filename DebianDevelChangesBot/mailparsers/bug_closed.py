#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2026 Sebastian Ramacher <sramacher@debian.org>
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

from . import MailParser, Message
from ..utils import tidy_bug_title, format_email_address

import re


SUBJECT = re.compile(r"^Bug#(\d+): marked as done \((.+)\)$")


class BugClosedMessage(Message):
    FIELDS = ("bug_number", "package", "by", "title")

    def format(self) -> str:
        return f"Closed [bug]#{self.bug_number}[/bug] in {self.package_name()} by [by]{self.by}[reset] «[title]{self.title}[reset]». [url]https://bugs.debian.org/{self.bug_number}[/url]"


class BugClosedParser(MailParser):
    @staticmethod
    def parse(headers, body, **kwargs) -> BugClosedMessage | None:
        if headers.get("List-Id", "") != "<debian-bugs-closed.lists.debian.org>":
            return

        m = SUBJECT.match(headers["Subject"])
        if not m:
            return

        msg = BugClosedMessage()
        msg.bug_number = int(m.group(1))
        msg.title = m.group(2)
        msg.by = headers["To"]

        # Bug was closed via 123456-done@bugs.debian.org, so To: is wrong.
        if "-done@bugs.debian.org" in msg.by:
            msg.by = headers["From"]

        # Let binary package name override source package
        msg.package = headers.get("X-Debian-PR-Source", None)
        msg.package = headers.get("X-Debian-PR-Package", msg.package)

        if msg.package is None:
            return

        msg.title = tidy_bug_title(msg.title, msg.package)
        msg.by = format_email_address(msg.by)

        return msg
