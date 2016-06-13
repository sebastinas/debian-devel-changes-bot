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
import socket
import urllib
import urllib2

from bs4 import BeautifulSoup

from DebianDevelChangesBot.messages import Popcon

socket.setdefaulttimeout(10)

def popcon(package, fileobj=None):
    if fileobj is None:
        fileobj = urllib2.urlopen(
            "https://qa.debian.org/popcon.php",
            urllib.urlencode({'package': package})
        )

    soup = BeautifulSoup(fileobj, "html.parser")
    rows = [x.string for x in soup('td')[1:]]

    msg = Popcon()
    msg.package = package
    msg.inst = int(rows[0])
    msg.vote = int(rows[3])
    msg.old = int(rows[6])
    msg.recent = int(rows[9])
    msg.nofiles = int(rows[12])

    return msg
