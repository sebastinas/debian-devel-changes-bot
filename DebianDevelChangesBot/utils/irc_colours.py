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

_TAGS = {
    "reset": chr(15),
    "b": chr(2),
    "/b": chr(2),
    "u": chr(31),
    "/u": chr(31),
    "black": chr(3) + "01",
    "darkblue": chr(3) + "02",
    "darkgreen": chr(3) + "03",
    "brightred": chr(3) + "04",
    "darkred": chr(3) + "05",
    "magenta": chr(3) + "06",
    "darkyellow": chr(3) + "07",
    "brightyellow": chr(3) + "08",
    "lightgreen": chr(3) + "09",
    "darkcyan": chr(3) + "10",
    "lightcyan": chr(3) + "11",
    "lightblue": chr(3) + "12",
    "pink": chr(3) + "13",
    "grey": chr(3) + "14",
    "white": chr(3) + "00",
    "nostyle": "",
}

# Stylesheet
_TAGS.update(
    {
        "by": _TAGS["lightcyan"],
        "package": _TAGS["darkgreen"],
        "pseudo-package": _TAGS["lightblue"],
        "version": _TAGS["darkcyan"],
        "distribution": _TAGS["lightblue"],
        "security": _TAGS["brightred"],
        "severity": _TAGS["brightred"],
        "urgency": _TAGS["brightred"],
        "new": _TAGS["brightred"],
        "section": _TAGS["grey"],
        "desc": _TAGS["nostyle"],
        "url": _TAGS["nostyle"],
        "/url": _TAGS["nostyle"],
        "bug": _TAGS["b"],
        "/bug": _TAGS["/b"],
        "title": _TAGS["nostyle"],
        "category": _TAGS["b"],
        "/category": _TAGS["/b"],
    }
)


def colourise(s):
    s = s + "[reset]"
    for k, v in _TAGS.items():
        s = s.replace("[%s]" % k, v)

    return s
