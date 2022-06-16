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

from .. import Message


class Popcon(Message):
    FIELDS = ("package", "inst", "vote", "old", "recent", "nofiles")

    def __init__(self, package, inst, vote, old, recent, nofiles):
        self.package = package
        self.inst = inst
        self.vote = vote
        self.old = old
        self.recent = recent
        self.nofiles = nofiles

    def format(self):
        msg = f"Popcon for [package]{self.package}[reset] - "
        for field in ("inst", "vote", "old", "recent", "nofiles"):
            msg += f"[category]{field}[/category]: {getattr(self, field)} "
        msg += f"- [url]https://qa.debian.org/developer.php?popcon={self.package}[/url]"
        return msg
