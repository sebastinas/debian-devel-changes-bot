#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2018 Sebastian Ramacher <sramacher@debian.org>
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

import requests


class DataSource:
    class DataError(Exception):
        pass

    def __init__(self, session: requests.Session | None):
        self.session = session if session is not None else requests.Session()


class MailParser:
    pass


from . import datasources

# FIXME: remove global state
pseudo_packages = datasources.PseudoPackages()


class Message:
    def __init__(self):
        if hasattr(self, "FIELDS"):
            for field in self.FIELDS:
                setattr(self, field, None)
        if hasattr(self, "OPTIONAL"):
            for field in self.OPTIONAL:
                setattr(self, field, None)

    def __bool__(self):
        if hasattr(self, "FIELDS"):
            for field in self.FIELDS:
                if getattr(self, field) is None:
                    return False
        return True

    def for_irc(self):
        return self.format()

    def package_name(self):
        if pseudo_packages.is_pseudo_package(self.package):
            return "[pseudo-package]%s[reset]" % self.package
        else:
            return "[package]%s[reset]" % self.package
