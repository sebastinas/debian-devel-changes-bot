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

class Popcon(Message):
    FIELDS = ('package', 'inst', 'vote', 'old', 'recent', 'nofiles')

    def format(self):
        msg = "Popcon for [package]%s[reset] - " % self.package

        for field in ('inst', 'vote', 'old', 'recent', 'nofiles'):
            msg += "[category]%s[/category]: %d " % (field, getattr(self, field))

        msg += "- [url]https://qa.debian.org/developer.php?popcon=%s[/url]" % self.package

        return msg
