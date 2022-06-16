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

import requests

from bs4 import BeautifulSoup
from ..messages.popcon import Popcon


def popcon(package, session=None):
    if session is None:
        session = requests.Session()

    response = session.get(
        "https://qa.debian.org/popcon.php", data={"package": package}
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = [x.string for x in soup("td")[1:]]

    return Popcon(
        package, int(rows[0]), int(rows[3]), int(rows[6]), int(rows[9]), int(rows[12])
    )
