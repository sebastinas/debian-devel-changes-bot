# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2016 Sebastian Ramacher <sramacher@debian.org>
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

import supybot.conf as conf
import supybot.registry as registry


def configure(advanced):
    conf.registerPlugin("DebianDevelChanges", True)


DebianDevelChanges = conf.registerPlugin("DebianDevelChanges")

conf.registerChannelValue(
    DebianDevelChanges,
    "package_regex",
    registry.Regexp(
        "", "Determines which package announcements should be printed to the channel"
    ),
)

conf.registerChannelValue(
    DebianDevelChanges,
    "maintainer_regex",
    registry.Regexp(
        "", "Determines which maintainer announcements should be printed to the channel"
    ),
)

conf.registerChannelValue(
    DebianDevelChanges,
    "distribution_regex",
    registry.Regexp(
        "",
        "Determines which distribution announcements should be printed to the channel",
    ),
)

conf.registerChannelValue(
    DebianDevelChanges,
    "send_privmsg",
    registry.Boolean(
        False, "Determines if PRIVMSG or NOTICE should be sent on " "the channel"
    ),
)

conf.registerGlobalValue(
    DebianDevelChanges,
    "apt_configuration_directory",
    registry.String("", "Determines path to apt config"),
)

conf.registerGlobalValue(
    DebianDevelChanges,
    "apt_cache_directory",
    registry.String("", "Determines path to apt cache"),
)
