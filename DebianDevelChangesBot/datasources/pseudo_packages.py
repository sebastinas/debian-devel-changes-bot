# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
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

import re

from DebianDevelChangesBot import NewDataSource


class PseudoPackage:
    def __init__(self, d, m):
        self.description = d
        self.maintainer = m


class PseudoPackages(NewDataSource):
    NAME = 'dinstall'
    URL_D = 'https://bugs.debian.org/pseudopackages/pseudo-packages.description'
    URL_M = 'https://bugs.debian.org/pseudopackages/pseudo-packages.maintainers'

    INTERVAL = 60 * 5

    def __init__(self, session=None):
        super().__init__(session)
        self.packages = {}
        self.regex = re.compile(r'([^\t ]*)[\t ]*(.*)')

    def update(self):
        response_d = self.session.get(self.URL_D)
        response_d.raise_for_status()
        response_m = self.session.get(self.URL_M)
        response_m.raise_for_status()

        descriptions = {}
        maintainers = {}

        for line in response_d.text.split('\n'):
            match = self.regex.match(line)
            if match:
                descriptions[match.group(1)] = match.group(2)

        for line in response_m.text.split('\n'):
            match = self.regex.match(line)
            if match:
                maintainers[match.group(1)] = match.group(2)

        package_names = set(descriptions.keys()).intersection(set(maintainers.keys()))

        packages = {}
        for package in package_names:
            packages[package] = PseudoPackage(descriptions[package], maintainers[package])
        self.packages = packages


    def pseudo_packages(self):
        return self.packages.keys()

    def is_pseudo_package(self, package):
        return package in self.packages

    def get_maintainer(self, package):
        if package not in self.packages:
            return None

        return self.packages[package].maintainer

    def get_description(self, package):
        if package not in self.packages:
            return None

        return self.packages[package].description
