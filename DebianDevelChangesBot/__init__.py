# -*- coding: utf-8 -*-
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


class PPWrapper:
    def __init__(self):
        self.pp = None

    def get_description(self, p):
        if self.pp is not None:
            return self.pp.get_description(p)
        return None

    def get_maintainer(self, p):
        if self.pp is not None:
            return self.pp.get_maintainer(p)
        return None

    def is_pseudo_package(self, p):
        if self.pp is not None:
            return self.pp.is_pseudo_package(p)
        return None

    def update(self):
        if self.pp is not None:
            self.pp.update()


pseudo_packages = PPWrapper()


class NewDataSource:
    class DataError(Exception):
        pass

    def __init__(self, session):
        self.session = session if session is not None else requests.Session()


class MailParser:
    pass


class Message:
    def __init__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                setattr(self, field, None)
        if hasattr(self, 'OPTIONAL'):
            for field in self.OPTIONAL:
                setattr(self, field, None)

    def __bool__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                if getattr(self, field) is None:
                    return False
        return True

    def for_irc(self):
        return self.format()

    def package_name(self):
        if pseudo_packages.is_pseudo_package(self.package):
            return '[pseudo-package]%s[reset]' % self.package
        else:
            return '[package]%s[reset]' % self.package


from . import utils
from . import messages
from . import datasources
from . import mailparsers

pseudo_packages.pp = datasources.PseudoPackages()
