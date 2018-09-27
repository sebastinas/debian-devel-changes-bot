# -*- coding: utf-8 -*-
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

import os
import apt_pkg

from DebianDevelChangesBot import pseudo_packages
from DebianDevelChangesBot import NewDataSource
from DebianDevelChangesBot.utils.decoding import split_address


class AptArchive(NewDataSource):
    # re-open cache every 30 min
    INTERVAL = 30 * 60
    NAME = "APT archive"

    def __init__(self, config_dir, state_dir):
        super().__init__(None)

        config = apt_pkg.config
        config["Dir::Etc"] = os.path.realpath(config_dir)
        config["Dir::State"] = os.path.join(os.path.realpath(state_dir), "state")
        config["Dir::Cache"] = os.path.join(os.path.realpath(state_dir), "cache")
        apt_pkg.init_config()
        apt_pkg.init_system()

        lists = apt_pkg.config.find_dir("Dir::State::Lists")
        os.makedirs(lists, exist_ok=True)
        os.makedirs(config["Dir::Cache"], exist_ok=True)

        self.cache = apt_pkg.Cache(None)
        self.depcache = apt_pkg.DepCache(self.cache)
        self.source_list = apt_pkg.SourceList()
        self.source_list.read_main_list()

    def update_index(self, ignore_errors=False):
        import apt.progress.base

        lists = apt_pkg.config.find_dir("Dir::State::Lists")
        with apt_pkg.FileLock(os.path.join(lists, "lock")):
            try:
                self.cache.update(apt.progress.base.AcquireProgress(), self.source_list)
            except apt_pkg.Error as e:
                if not ignore_errors:
                    raise NewDataSourc.DataError("Failed to update cache: {}".format(e))

    def update(self):
        self.cache = apt_pkg.Cache(None)
        self.depcache = apt_pkg.DepCache(self.cache)

    def get_maintainer(self, package):
        maintainer = pseudo_packages.get_maintainer(package)
        if maintainer is not None:
            return split_address(maintainer)

        if package in self.cache:
            candidate = self.depcache.get_candidate_ver(self.cache[package])
            if candidate is not None:
                records = apt_pkg.PackageRecords(self.cache)
                if records.lookup(candidate.file_list[0]):
                    return split_address(records.maintainer)

                # delete record iterator
                del records

        if package.startswith("src:"):
            package = package[4:]

        records = apt_pkg.SourceRecords()
        if records.lookup(package):
            version = records.version
            maintainer = records.maintainer
            while records.lookup(package) is not None:
                if apt_pkg.version_compare(records.version, version) > 0:
                    version = records.version
                    maintainer = records.maintainer

            return split_address(maintainer)

        raise NewDataSource.DataError(
            "Unable to get maintainer for {}.".format(package)
        )
