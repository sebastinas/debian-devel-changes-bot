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

import urllib2

import socket
socket.setdefaulttimeout(10)

# Synced from http://bugs.debian.org/pseudopackages/pseudo-packages.description
pseudo_packages = {
    'base': 'Base system general bugs',
    'cdrom': 'Installation system',
    'spam': 'Spam (reassign spam to here so we can complain about it)',
    'press': 'Press release issues',
    'project': 'Problems related to project administration',
    'general': 'General problems (e.g. "many manpages are mode 755")',
    'nm.debian.org': 'New Maintainer process and nm.debian.org webpages',
    'qa.debian.org': 'The Quality Assurance group',
    'ftp.debian.org': 'Problems with the FTP site',
    'www.debian.org': 'Problems with the WWW site',
    'bugs.debian.org': 'The bug tracking system, @bugs.debian.org',
    'lists.debian.org': 'The mailing lists, debian-*@lists.debian.org',
    'wnpp': 'Work-Needing and Prospective Packages list',
    'cdimage.debian.org': 'CD Image issues',
    'tech-ctte': 'The Debian Technical Committee (see the Constitution)',
    'mirrors': 'Problems with the official mirrors',
    'security.debian.org': 'The Debian Security Team',
    'installation-reports': 'Reports of installation problems with stable & testing',
    'upgrade-reports': 'Reports of upgrade problems for stable & testing',
    'release-notes': 'Problems with the Release Notes',
    'wiki.debian.org': 'Problems with the Debian wiki',
    'security-tracker': 'The Debian Security Bug Tracker',
    'release.debian.org': 'Requests regarding Debian releases and release team tools',
    'debian-i18n': 'Requests regarding Internationalization (i18n) of the distribution',
    'buildd.emdebian.org': 'Problems related to building packages for Emdebian',
    'buildd.debian.org': 'Problems and requests related to the Debian Buildds',
    'debian-maintainers': 'Problems and requests related to Debian Maintainers',
    'snapshot.debian.org': 'Issues with the snapshot.debian.org service',
}

class Datasource(object):
    class DataError(Exception):
        pass

    def update(self):
        fileobj = urllib2.urlopen(self.URL)
        return self.parse(fileobj)

class MailParser(object):
    pass

class Message(object):
    def __init__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                setattr(self, field, None)
        if hasattr(self, 'OPTIONAL'):
            for field in self.OPTIONAL:
                setattr(self, field, None)

    def __nonzero__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                if getattr(self, field) is None:
                    return False
        return True

    def for_irc(self):
        return self.format().encode('utf-8')

    def package_name(self):
        if self.package in pseudo_packages.keys():
            return '[pseudo-package]%s[reset]' % self.package
        else:
            return '[package]%s[reset]' % self.package

import utils
import messages
import datasources
import mailparsers

reload(utils)
reload(messages)
reload(datasources)
reload(mailparsers)
