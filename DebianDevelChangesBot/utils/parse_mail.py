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

import email

from DebianDevelChangesBot.utils import quoted_printable

def parse_mail(fileobj):
    headers, body = {}, []
    msg = email.message_from_file(fileobj)

    for k, v in msg.items():
        headers[k] = quoted_printable(v).replace('\n', '').replace('\t', ' ').strip()

    for line in email.Iterators.body_line_iterator(msg):
        line = unicode(line, 'utf-8', 'replace').replace('\n', '')
        body.append(line)

    # Merge lines joined with "=\n"
    i = len(body) - 1
    while i > 0:
        i -= 1
        prev = body[i]
        if len(prev) == 74 and prev.endswith('='):
            body[i] = body[i][:-1] + body[i + 1]
            del body[i + 1]

    # Remove =20 from end of lines
    i = 0
    while i < len(body):
        if body[i].endswith('=20'):
            body[i] = body[i][:-3] + ' '
        i += 1

    return headers, body
