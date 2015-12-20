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

import requests

from BeautifulSoup import BeautifulSoup

from DebianDevelChangesBot import NewDataSource


class Maintainer(NewDataSource):
    URL = 'http://packages.qa.debian.org/%s/%s.html'

    def __init__(self, session=None):
        super(Maintainer, self).__init__(session)

    @classmethod
    def get_pool_url(cls, package):
        if package.startswith('src:'):
            package = package[4:]

        if package.startswith('lib'):
            urls = (package[:4], package)
        else:
            urls = (package[:1], package)
        return cls.URL % urls

    def get_maintainer(self, package):
        response = self.session.get(self.get_pool_url(package))
        if response.status_code == requests.codes.NOT_FOUND:
            # Package does not exist
            return None

        response.raise_for_status()

        soup = BeautifulSoup(response.text)
        base = soup.find('span', {'class': 'name', 'title': 'maintainer'})

        try:
            return {
                'name': base.string,
                'email': base.parent['href'].split('=', 1)[1],
            }
        except AttributeError:
            raise Datasource.DataError(
                'Unable to get maintainer for %s.' % package)
