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

# Import these directly due to funkiness in Python 2.4's email library
import email.Header
import email.quopriMIME

def header_decode(s):
    def unquote_match(match):
        s = match.group(0)
        return chr(int(s[1:3], 16))

    s = s.replace('_', ' ')
    return re.sub(r'=\w{2}', unquote_match, s)

def quoted_printable(val):
    try:
        if type(val) is str:
            save = header_decode(val)

            # Hack around possible bug in email.Header.decode_header
            val = val.replace('?=)', '?= )')

            val = ' '.join([chunk.decode(encoding or 'ascii', 'replace') for chunk, encoding in
                email.Header.decode_header(val)])

            val = val.replace(' )', ')')

            if len(val) > len(save):
                val = unicode(save, 'utf-8', 'replace')

        else:
            return unicode(email.quopriMIME.header_decode(str(val)), 'utf-8', 'replace')

    except Exception as e:
        # We ignore errors here. Most of these originate from a spam
        # report adding a synopsis of a message with broken encodings.
        pass

    return val
