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

from debian_bundle.deb822 import Deb822
from DebianDevelChangesBot import NewDataSource


class NewQueue(NewDataSource):
    NAME = "NEW queue"
    URL = "https://ftp-master.debian.org/new.822"
    INTERVAL = 60 * 30

    def __init__(self, session=None):
        super().__init__(session)
        self.packages = {}
        self.backports_packages = {}
        self.fetched = False

    def update(self):
        response = self.session.get(self.URL)
        response.raise_for_status()
        data = response.text

        packages = {}
        backports_packages = {}

        for para in Deb822.iter_paragraphs(data):
            pkg = para["Source"]
            queue = para["Queue"]
            if queue == "new":
                packages[pkg] = para["Version"].split(" ")
            if queue == "backports-new":
                backports_packages[pkg] = para["Version"].split(" ")

        self.packages = packages
        self.backports_packages = backports_packages
        self.fetched = True

    def check_version(self, packages, package, version):
        versions = packages.get(package, [])
        return version in versions

    def is_new(self, package, version):
        return self.check_version(self.packages, package, version)

    def is_backports_new(self, package, version):
        return self.check_version(self.backports_packages, package, version)

    def get_size(self):
        if not self.fetched:
            return None
        return len(self.packages)

    def get_backports_size(self):
        if not self.fetched:
            return None
        return len(self.backports_packages)
