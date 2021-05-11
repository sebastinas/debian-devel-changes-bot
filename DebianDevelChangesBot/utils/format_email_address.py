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

EMAIL = re.compile(r"^(.*) ?(<.+@.+>)$")
EMAIL_ALT = re.compile(r"^<?([^@]+@[^\s>]+)>? \((.*)\)$")
DEBIAN_EMAIL = re.compile(r"^<([-a-z0-9]+)@(?:merkel\.|master\.)?debian.org>$")

WHITESPACE = re.compile(r"\s{2,}")
CONTINUATION = re.compile(r"\.{3,}$")


def format_email_address(input, max_user=13, max_domain=10):
    m = EMAIL_ALT.match(input)
    if m:
        input = f"{m.group(2)} <{m.group(1)}>"

    m = EMAIL.match(input)
    if not m:
        return input

    # Name
    name = m.group(1).strip()
    name = WHITESPACE.sub(" ", name)

    # Remove quotes around name
    for quote in ("'", '"'):
        if len(name) > 0 and name[0] == quote and name[-1] == quote:
            name = name[1:-1]

    # Email address
    address = m.group(2).lower().replace(" ", "")
    address = WHITESPACE.sub(" ", address)

    # Fix broken '"foo@bar.com" <foo@bar.com>' mail addresses
    if input == f'"{name}" <{name}>':
        return address

    if DEBIAN_EMAIL.match(address):
        address = DEBIAN_EMAIL.sub(r"(\1)", address)

        # Remove duplications of Debian user suffixed to name
        if name.lower().endswith(address.lower()):
            name = name[: -len(address) - 1]

    else:
        # Shorten email address
        user, host = address[1:-1].split("@")
        if len(user) > max_user:
            user = "%s..." % user[: max(max_user - 3, 0)]
        if len(host) > max_domain:
            host = "%s..." % host[: max(max_domain - 3, 0)]

        # Normalise triple-dots
        user = CONTINUATION.sub("...", user)
        host = CONTINUATION.sub("...", host)

        address = f"<{user}@{host}>"

    ret = f"{name} {address}"
    return ret.strip()
