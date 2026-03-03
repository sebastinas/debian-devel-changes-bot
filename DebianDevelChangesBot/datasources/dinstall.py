#
#   Debian Changes Bot
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

from . import DataSource


class Dinstall(DataSource):
    URL = "https://ftp-master.debian.org/dinstall.status"

    @staticmethod
    def interval() -> int:
        return 60 * 5

    @staticmethod
    def name() -> str:
        return "dinstall"

    def __init__(self, session: requests.Session) -> None:
        super().__init__()
        self.session = session
        self.status = "not running"

    def update(self) -> None:
        response = self.session.get(self.URL)
        response.raise_for_status()

        data = response.text
        self.status = "not running"
        for line in data.split("\n"):
            if not line.startswith("Current action"):
                continue

            if line != "Current action: all done":
                self.status = line[len("Current action: ") :]

            break

    def get_status(self) -> str:
        return self.status
