# -*- coding: utf-8 -*-
#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
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

import requests


# curl -qs https://bugs.debian.org/pseudopackages/pseudo-packages.description | sed -e 's@\([^\t ]*\)[\t ]*\(.*\)@    '\''\1'\'': "\2"\,@g'
pseudo_packages = {
    'base': "(Deprecated; do not assign bugs) Base system general bugs",
    'cdrom': "Installation system",
    'spam': "Spam (reassign spam to here so we can complain about it)",
    'press': "Press release issues",
    'project': "Problems related to project administration",
    'general': "General problems (e.g. \"many manpages are mode 755\")",
    'nm.debian.org': "New Member process and nm.debian.org webpages",
    'qa.debian.org': "The Quality Assurance group",
    'ftp.debian.org': "Problems with the FTP site",
    'www.debian.org': "Problems with the WWW site",
    'bugs.debian.org': "The bug tracking system, @bugs.debian.org",
    'lists.debian.org': "The mailing lists, debian-*@lists.debian.org",
    'wnpp': "Work-Needing and Prospective Packages list",
    'cdimage.debian.org': "CD Image issues",
    'tech-ctte': "The Debian Technical Committee (see the Constitution)",
    'mirrors': "Problems with the official mirrors",
    'security.debian.org': "The Debian Security Team",
    'installation-reports': "Reports of installation problems with stable & testing",
    'upgrade-reports': "Reports of upgrade problems for stable & testing",
    'release-notes': "Problems with the Release Notes",
    'wiki.debian.org': "Problems with the Debian wiki",
    'security-tracker': "The Debian Security Bug Tracker",
    'release.debian.org': "Requests regarding Debian releases and release team tools",
    'debian-i18n': "Requests regarding Internationalization (i18n) of the distribution",
    'buildd.emdebian.org': "Problems related to building packages for Emdebian",
    'buildd.debian.org': "Problems and requests related to the Debian Buildds",
    'debian-maintainers': "Problems and requests related to Debian Maintainers",
    'snapshot.debian.org': "Issues with the snapshot.debian.org service ",
    'sponsorship-requests': "Requests for package review and sponsorship",
    'debian-live': "General problems with Debian Live systems",
    'pet.debian.net': "The Debian Package Entropy Tracker",
    'cloud.debian.org': "Issues involving Debian images for public/private clouds",
    'piuparts.debian.org': "Issues with the piuparts.debian.org service",
    'sso.debian.org': "Problems and requests related to the Debian Single Sign On system",
    'tracker.debian.org': "Issues with the Debian Package Tracker and coordination of its maintenance",
    'd-i.debian.org': "Issues regarding the d-i.debian.org service and general Debian Installer tasks",
    'summit.debconf.org': "Problems and requests related to the DebConf Summit instance",
    'rtc.debian.org': "Issues in the operation of the Debian RTC services which are not package-specific bugs",
    'jenkins.debian.org': "Issues with the jenkins.debian.org service",
    'manpages.debian.org': "Issues with the Debian Manpages Website and coordination of maintenance",
}

# curl -qs https://bugs.debian.org/pseudopackages/pseudo-packages.maintainers | sed -e 's@\([^\t ]*\)[\t ]*\(.*\)@    '\''\1'\'': "\2"\,@g'
pseudo_package_maintainers = {
    'base': "Base Maintainers <virtual-pkg-base-maintainers@lists.alioth.debian.org>",
    'cdrom': "Debian CD-ROM Team <debian-cd@lists.debian.org>",
    'press': "press@debian.org",
    'bugs.debian.org': "Debian Bug Tracking Team <owner@bugs.debian.org>",
    'ftp.debian.org': "Debian FTP Master <ftpmaster@ftp-master.debian.org>",
    'nm.debian.org': "New Member Front-Desk <nm@debian.org>",
    'qa.debian.org': "debian-qa@lists.debian.org",
    'www.debian.org': "Debian WWW Team <debian-www@lists.debian.org>",
    'mirrors': "Debian Mirrors Team <mirrors@debian.org>",
    'project': "debian-project@lists.debian.org",
    'general': "debian-devel@lists.debian.org",
    'lists.debian.org': "Debian Listmaster Team <listmaster@lists.debian.org>",
    'spam': "spam@debian.org",
    'wnpp': "wnpp@debian.org",
    'cdimage.debian.org': "Debian CD-ROM Team <debian-cd@lists.debian.org>",
    'tech-ctte': "Technical Committee <debian-ctte@lists.debian.org>  ",
    'security.debian.org': "Debian Security Team <team@security.debian.org>",
    'installation-reports': "Debian Install Team <debian-boot@lists.debian.org>",
    'upgrade-reports': "Debian Testing Group <debian-testing@lists.debian.org>",
    'release-notes': "Debian Documentation Team <debian-doc@lists.debian.org>",
    'wiki.debian.org': "Debian WWW Team <debian-www@lists.debian.org>",
    'security-tracker': "Debian Security Tracker Team <debian-security-tracker@lists.debian.org>",
    'release.debian.org': "Debian Release Team <debian-release@lists.debian.org>",
    'debian-i18n': "Debian I18N Team <debian-i18n@lists.debian.org>",
    'buildd.emdebian.org': "Debian Embedded Team <debian-embedded@lists.debian.org>",
    'buildd.debian.org': "Debian Buildd Team <wb-team@buildd.debian.org>",
    'debian-maintainers': "Debian Maintainer Keyring Team <debian-maintainers@nm.debian.org>",
    'snapshot.debian.org': "snapshot.debian.org Team <debian-snapshot@lists.debian.org>",
    'sponsorship-requests': "Debian Mentors <package-sponsorship-requests@lists.debian.org>",
    'debian-live': "Debian Live Project <debian-live@lists.debian.org>",
    'pet.debian.net': "PET developers <pet-devel@lists.alioth.debian.org>",
    'cloud.debian.org': "Debian Cloud Team <debian-cloud@lists.debian.org>",
    'piuparts.debian.org': "Piuparts Developers <piuparts-devel@lists.alioth.debian.org>",
    'sso.debian.org': "Debian SSO Team <debian-www@lists.debian.org>",
    'tracker.debian.org': "Debian QA Team <debian-qa@lists.debian.org>",
    'd-i.debian.org': "Debian Installer <debian-boot@lists.debian.org>",
    'summit.debconf.org': "Debconf Infrastructure Team <debconf-infra@lists.debian.org>",
    'rtc.debian.org': "Debian RTC Team <debian-rtc-admin@lists.alioth.debian.org>",
    'jenkins.debian.org': "Debian Jenkins Team <qa-jenkins-dev@lists.alioth.debian.org>",
    'manpages.debian.org': "Manpages Website Maintainers <debian-doc@lists.debian.org>",
}


class NewDataSource:
    class DataError(Exception):
        pass

    def __init__(self, session):
        self.session = session if session is not None else requests.Session()


class MailParser:
    pass


class Message:
    def __init__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                setattr(self, field, None)
        if hasattr(self, 'OPTIONAL'):
            for field in self.OPTIONAL:
                setattr(self, field, None)

    def __bool__(self):
        if hasattr(self, 'FIELDS'):
            for field in self.FIELDS:
                if getattr(self, field) is None:
                    return False
        return True

    def for_irc(self):
        return self.format()

    def package_name(self):
        if self.package in pseudo_packages.keys():
            return '[pseudo-package]%s[reset]' % self.package
        else:
            return '[package]%s[reset]' % self.package


from . import utils
from . import messages
from . import datasources
from . import mailparsers
