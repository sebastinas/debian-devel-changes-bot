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

import os
import sys
import supybot

__version__ = "2"
__author__ = supybot.Author("Sebastian Ramacher", "Sebastinas", "sramacher@debian.org")
__contributors__ = {
    supybot.Author("Chris Lamb", "lamby", "chris@chris-lamb.co.uk"): (
        "Initial version",
    )
}
__url__ = "https://github.com/sebastinas/debian-devel-changes-bot/"

basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if basedir not in sys.path:
    sys.path.append(basedir)

import DebianDevelChangesBot

from . import config
from . import plugin

Class = plugin.Class
configure = config.configure
