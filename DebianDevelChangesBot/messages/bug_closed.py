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


class BugClosedMessage(Message):
    FIELDS = ("bug_number", "package", "by", "title")

    def format(self):
        return f"Closed [bug]#{self.bug_number}[/bug] in {self.package_name()} by [by]{self.by}[reset] «[title]{self.title}[reset]». [url]https://bugs.debian.org/{self.bug_number}[/url]"
