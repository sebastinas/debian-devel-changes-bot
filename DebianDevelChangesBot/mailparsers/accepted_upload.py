#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyirhgt (C) 2026 Sebastian Ramacher <sramacher@debian.org>
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
from ..utils import quoted_printable, format_email_address


LISTS = (
    "<debian-devel-changes.lists.debian.org>",
    "<debian-backports-changes.lists.debian.org>",
    "<debian-lts-changes.lists.debian.org>",
    "<debian-changes.lists.debian.org>",
)


class AcceptedUploadMessage(Message):
    FIELDS = ("package", "version", "distribution", "urgency", "by", "maintainer")
    OPTIONAL = ("closes", "new_upload")

    def format(self) -> str:
        msg = f"{self.package_name()} "
        if self.new_upload:
            msg += "[new](NEW)[reset] "
        msg += f"[version]{self.version}[reset] uploaded "
        if self.distribution not in ("unstable", "sid"):
            msg += f"to [distribution]{self.distribution}[reset] "
        if self.urgency == "high":
            msg += "with urgency [urgency]high[reset] "
        msg += f"by [by]{self.by}[reset] "
        if self.closes and "-backports" not in self.distribution:
            bug_list = ", ".join(f"[bug]#{x}[/bug]" for x in self.closes)
            msg += f"(Closes: {bug_list}) "
        msg += f"[url]https://tracker.debian.org/{self.package}[/url]"
        return msg


class AcceptedUploadParser(MailParser):
    @staticmethod
    def parse(headers, body, **kwargs) -> AcceptedUploadMessage | None:
        if headers.get("List-Id", "") not in LISTS:
            return

        mapping = {
            "Source": "package",
            "Version": "version",
            "Distribution": "distribution",
            "Urgency": "urgency",
            "Changed-By": "by",
            "Closes": "closes",
            "Maintainer": "maintainer",
        }

        msg = AcceptedUploadMessage()
        for line in body:
            for field, target in mapping.items():
                if line.startswith(f"{field}: "):
                    val = line[len(field) + 2 :]
                    setattr(msg, target, val)
                    del mapping[field]
                    break

            # If we have found all the fields, stop looking
            if len(mapping) == 0:
                break

        if msg.by:
            msg.by = format_email_address(quoted_printable(msg.by))

        try:
            if msg.closes:
                msg.closes = [int(x) for x in msg.closes.split(" ")]
        except ValueError:
            return

        if msg.urgency:
            msg.urgency = msg.urgency.lower()

        if "new_queue" in kwargs:
            new_queue = kwargs["new_queue"]
            msg.new_upload = new_queue.is_new(
                msg.package, msg.version
            ) or new_queue.is_backports_new(msg.package, msg.version)

        return msg
