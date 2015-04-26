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

import threading
import urllib2
import json

from DebianDevelChangesBot import Datasource

class TestingRCBugs(Datasource):
    _shared_state = {}

    URL = 'http://udd.debian.org/bugs.cgi?release=stretch&notmain=ign&merged=ign&rc=1&format=json'
    INTERVAL = 60 * 20

    lock = threading.Lock()
    bugs = None

    def __init__(self):
        self.__dict__ = self._shared_state

    def update(self, fileobj=None):
        if fileobj is None:
            fileobj = urllib2.urlopen(self.URL)

        try:
            data = json.load(fileobj)
        except ValueError:
            raise Datasource.DataError()

        bugs = set()
        for bug in data:
            try:
                bugs.add(bug['id'])
            except KeyError:
                pass

        if bugs:
            with self.lock:
                self.bugs = bugs
        else:
            # Zarro bugs found; probably an error.
            raise Datasource.DataError()

    def get_bugs(self):
        with self.lock:
            return self.bugs
