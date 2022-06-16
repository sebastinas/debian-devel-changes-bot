#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2015 Sebastian Ramacher <sramacher@debian.org>
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


class AcceptedUploadMessage(Message):
    FIELDS = ("package", "version", "distribution", "urgency", "by", "maintainer")
    OPTIONAL = ("closes", "new_upload")

    def format(self):
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
