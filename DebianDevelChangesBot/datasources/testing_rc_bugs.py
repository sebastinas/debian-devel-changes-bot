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
import requests

from DebianDevelChangesBot import NewDataSource


class RCBugs(NewDataSource):
    INTERVAL = 60 * 20
    URL = 'http://udd.debian.org/bugs.cgi'

    def __init__(self, suite, session=None):
        super(RCBugs, self).__init__(session)
        self.suite = suite
        self.bugs = None

    def update(self):
        payload = {
            'release': self.suite,
            'notmain': 'ign',
            'merged': 'ign',
            'rc': 1,
            'format': 'json'
        }

        response = self.session.get(self.URL, params=payload)
        try:
            data = response.json()
        except ValueError:
            raise Datasource.DataError()

        bugs = set()
        for bug in data:
            try:
                bugs.add(bug['id'])
            except KeyError:
                pass

        if bugs:
            self.bugs = bugs
        else:
            raise Datasource.DataError()

    def get_bugs(self):
        return self.bugs

    def get_number_bugs(self):
        if self.bugs is not None:
            return len(self.bugs)
        else:
            return None


class TestingRCBugs(RCBugs):
    def __init__(self, session=None):
        super(TestingRCBugs, self).__init__('stretch', session)


class StableRCBugs(RCBugs):
    def __init__(self, session=None):
        super(StableRCBugs, self).__init__('jessie', session)
