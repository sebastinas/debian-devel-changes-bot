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
import thread
import urllib2

from BeautifulSoup import BeautifulSoup

import socket
socket.setdefaulttimeout(10)

from DebianDevelChangesBot import Datasource

class TestingRCBugs(Datasource):
    _shared_state = {}

    URL = 'http://bts.turmzimmer.net/details.php?bydist=wheezy&igncontrib=on&ignnonfree=on'
    INTERVAL = 60 * 10

    lock = thread.allocate_lock()
    bugs = None

    def __init__(self):
        self.__dict__ = self._shared_state

    def update(self, fileobj=None):
        if fileobj is None:
            fileobj = urllib2.urlopen(self.URL)

        soup = BeautifulSoup(fileobj)

        bugs = set()

        for link in soup('a'):
            bug = link.get('name', '')
            try:
                bugs.add(int(bug))
            except ValueError:
                pass

        if bugs:
            self.lock.acquire()
            try:
                self.bugs = bugs
            finally:
                self.lock.release()
        else:
            # Zarro bugs found; probably an error.
            raise Datasource.DataError()

    def get_bugs(self):
        self.lock.acquire()
        try:
            return self.bugs
        finally:
            self.lock.release()
