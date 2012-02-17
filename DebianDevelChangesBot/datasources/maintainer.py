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

import thread
import urllib2
from BeautifulSoup import BeautifulSoup

import socket
socket.setdefaulttimeout(10)

from DebianDevelChangesBot import Datasource

class Maintainer(Datasource):
    _shared_state = {}

    packages = {}
    lock = thread.allocate_lock()

    def __init__(self):
        self.__dict__ = self._shared_state

    def get_maintainer(self, package, fileobj=None):
        info = {}

        self.lock.acquire()
        try:
            if fileobj is None:
                def get_pool_url(package):
                    if package.startswith('lib'):
                        return (package[:4], package)
                    else:
                        return (package[:1], package)
                try:
                    fileobj = urllib2.urlopen("http://packages.qa.debian.org/%s/%s.html" % get_pool_url(package))
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        # Package does not exist
                        return None
                    else:
                        raise

            soup = BeautifulSoup(fileobj)

            base = soup.find('span', {'class': 'name', 'title': 'maintainer'})
            info['name'] = base.string
            info['email'] = base.parent['href'].split('=', 1)[1]

        finally:
            self.lock.release()

        return info
