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

import re

import email.header
import email.quoprimime
import email.utils


def header_decode(s):
    def unquote_match(match):
        s = match.group(0)
        return chr(int(s[1:3], 16))

    s = s.replace("_", " ")
    return re.sub(r"=\w{2}", unquote_match, s)


def _decode_chunk(chunk, encoding):
    if encoding is None:
        if isinstance(chunk, bytes):
            return chunk.decode("ascii")
        else:
            return chunk
    else:
        return chunk.decode(encoding)


def quoted_printable(val):
    try:
        if type(val) is str:
            save = header_decode(val)

            val = "".join(
                [
                    _decode_chunk(chunk, encoding)
                    for chunk, encoding in email.header.decode_header(val)
                ]
            )

            val = val.replace(" )", ")")

            if len(val) > len(save):
                val = save.encode("latin1").decode("utf-8", "replace")

        else:
            return email.quoprimime.header_decode(str(val))

    except Exception as e:
        # We ignore errors here. Most of these originate from a spam
        # report adding a synopsis of a message with broken encodings.
        if not isinstance(e, ValueError) or "invalid literal" not in str(e):
            raise

    return val


def split_address(addr):
    name, addr = email.utils.parseaddr(addr)
    return {"name": name, "email": addr}
