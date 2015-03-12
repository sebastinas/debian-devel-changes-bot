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

import re
import threading
import urllib2

import socket
socket.setdefaulttimeout(10)

from DebianDevelChangesBot import Datasource

MATCHER = re.compile(r'<div class="subject">([^:]+): ')

class RmQueue(Datasource):
    _shared_state = {}

    URL = 'http://ftp-master.debian.org/removals.html'
    INTERVAL = 60 * 30

    packages = set()
    lock = threading.Lock()

    def __init__(self):
        self.__dict__ = self._shared_state

    def update(self, fileobj=None):
        if fileobj is None:
            fileobj = urllib2.urlopen(self.URL)

        packages = MATCHER.findall(fileobj.read())

        with self.lock:
            self.packages = packages

    def get_size(self):
        with self.lock:
            size = len(self.packages)
            if size > 0:
                return size
            return None

    def is_rm(self, pkg):
        with self.lock:
            return pkg in self.packages
