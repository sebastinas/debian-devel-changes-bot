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

WHITESPACE = re.compile(r"\s{2,}")


def tidy_bug_title(title, package):
    """
    Strips various package name prefixes from a bug title.

    For example:

      "emacs: Not as good as vim"  =>  "Not as good as vim"
      "[emacs] Not as good as vim"  =>  "Not as good as vim"

    """

    title = title.strip()

    for prefix in ("Subject: ", "%s: ", "[%s]: ", "[%s] "):
        try:
            prefix = prefix % package
        except:
            pass

        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix) :]

    title = WHITESPACE.sub(" ", title)

    return title.strip()
