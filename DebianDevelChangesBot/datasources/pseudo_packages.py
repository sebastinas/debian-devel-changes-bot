#
#   Debian Changes Bot
#   Copyright (C) 2018 Sebastian Ramacher <sramacher@debian.org>
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
import requests
from importlib import resources
from dataclasses import dataclass

from . import DataSource


@dataclass
class PseudoPackage:
    description: str
    maintainer: str


REGEX = re.compile(r"([^\t ]*)[\t ]*(.*)")


def parse(descriptions_data: str, maintainers_data: str) -> dict[str, PseudoPackage]:
    descriptions = {}
    maintainers = {}

    for line in descriptions_data.split("\n"):
        match = REGEX.match(line)
        if match:
            descriptions[match.group(1)] = match.group(2)

    for line in maintainers_data.split("\n"):
        match = REGEX.match(line)
        if match:
            maintainers[match.group(1)] = match.group(2)

    package_names = set(descriptions.keys()).intersection(set(maintainers.keys()))

    packages = {}
    for package in package_names:
        packages[package] = PseudoPackage(descriptions[package], maintainers[package])
    return packages


class PseudoPackages(DataSource):
    NAME = "pseudo packages"
    URL_D = "https://bugs.debian.org/pseudopackages/pseudo-packages.description"
    URL_M = "https://bugs.debian.org/pseudopackages/pseudo-packages.maintainers"

    INTERVAL = 60 * 5

    def __init__(self, session: requests.Session | None = None) -> None:
        super().__init__()

        self.session = session
        self.packages = parse(
            resources.read_text(
                "DebianDevelChangesBot.datasources", "pseudo-packages.description"
            ),
            resources.read_text(
                "DebianDevelChangesBot.datasources", "pseudo-packages.maintainers"
            ),
        )

    def update(self) -> None:
        assert self.session is not None

        response_d = self.session.get(self.URL_D)
        response_d.raise_for_status()
        response_m = self.session.get(self.URL_M)
        response_m.raise_for_status()

        self.packages = parse(response_d.text, response_m.text)

    def pseudo_packages(self):
        return self.packages.keys()

    def is_pseudo_package(self, package) -> bool:
        return package in self.packages

    def get_maintainer(self, package) -> str | None:
        if package not in self.packages:
            return None

        return self.packages[package].maintainer

    def get_description(self, package) -> str | None:
        if package not in self.packages:
            return None

        return self.packages[package].description
