# -*- coding: utf-8 -*-
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
    NAME = 'NEW queue'
    URL = 'https://ftp-master.debian.org/new.822'
    INTERVAL = 60 * 30

    def __init__(self, session=None):
        super(NewQueue, self).__init__(session)
        self.packages = {}

    def update(self):
        response = self.session.get(self.URL)
        response.raise_for_status()
        data = response.text

        packages = {}
        for para in Deb822.iter_paragraphs(data):
            pkg = para['Source']
            if para['Queue'] == 'new':
                packages[pkg] = para['Version'].split(' ')

        self.packages = packages

    def is_new(self, package, version):
        versions = self.packages.get(package, [])
        return version in versions

    def get_size(self):
        size = len(self.packages)
        if size > 0:
            return size
        return None
