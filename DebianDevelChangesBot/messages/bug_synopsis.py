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


class BugSynopsis(Message):
    FIELDS = ('bug_number', 'package', 'status', 'title', 'severity')

    def format(self):
        msg = "[bug]#%d[/bug]" % self.bug_number

        if self.status == 'done':
            msg += " (fixed)"

        msg += ": %s: «[title]%s[reset]» " % (self.package_name(), self.title)

        if self.severity != 'normal':
            if self.severity in ('critical', 'grave', 'serious'):
                msg += "([severity]%s[reset]) " % self.severity
            else:
                msg += "(%s) " % self.severity

        msg += "[url]https://bugs.debian.org/%d[/url]" % self.bug_number

        return msg
