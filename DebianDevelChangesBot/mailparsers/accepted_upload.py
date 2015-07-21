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

from DebianDevelChangesBot import MailParser
from DebianDevelChangesBot.utils import quoted_printable, format_email_address
from DebianDevelChangesBot.messages import AcceptedUploadMessage


lists = (
    '<debian-devel-changes.lists.debian.org>',
    '<debian-backports-changes.lists.debian.org>'
)


class AcceptedUploadParser(MailParser):

    @staticmethod
    def parse(headers, body, **kwargs):
        if headers.get('List-Id', '') not in lists:
            return

        mapping = {
            'Source': 'package',
            'Version': 'version',
            'Distribution': 'distribution',
            'Urgency': 'urgency',
            'Changed-By': 'by',
            'Closes': 'closes',
            'Maintainer': 'maintainer'
        }

        msg = AcceptedUploadMessage()
        for line in body:
            for field, target in mapping.iteritems():
                if line.startswith('%s: ' % field):
                    val = line[len(field) + 2:]
                    setattr(msg, target, val)
                    del mapping[field]
                    break

            # If we have found all the fields, stop looking
            if len(mapping) == 0:
                break

        if msg.by:
            msg.by = format_email_address(quoted_printable(msg.by))

        try:
            if msg.closes:
                msg.closes = [int(x) for x in msg.closes.split(' ')]
        except ValueError:
            return

        if msg.urgency:
            msg.urgency = msg.urgency.lower()

        if msg.maintainer:
            msg.maintainer = format_email_address(quoted_printable(msg.by))

        if 'new_queue' in kwargs:
            new_queue = kwargs['new_queue']
            msg.new_upload = new_queue.is_new(msg.package, msg.version)

        return msg
