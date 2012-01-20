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

import os
import re
import time
import random
import urllib
import supybot
import threading

from supybot.commands import wrap, many
from supybot import ircdb, log, schedule

from DebianDevelChangesBot.mailparsers import get_message
from DebianDevelChangesBot.datasources import get_datasources, TestingRCBugs, \
    NewQueue, RmQueue, Maintainer
from DebianDevelChangesBot.utils import parse_mail, FifoReader, colourise, \
    rewrite_topic, madison, bug_synopsis, format_email_address, popcon

class DebianDevelChanges(supybot.callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(DebianDevelChanges, self)
        self.__parent.__init__(irc)
        self.irc = irc
        self.topic_lock = threading.Lock()

        fr = FifoReader()
        fifo_loc = '/var/run/debian-devel-changes/fifo'
        fr.start(self._email_callback, fifo_loc)

        self.queued_topics = {}
        self.last_n_messages = []

        # Schedule datasource updates
        for klass, interval, name in get_datasources():
            try:
                schedule.removePeriodicEvent(name)
            except KeyError:
                pass

            def wrapper(klass=klass):
                klass().update()
                self._topic_callback()

            schedule.addPeriodicEvent(wrapper, interval, name, now=False)
            schedule.addEvent(wrapper, time.time() + 1)

    def die(self):
        FifoReader().stop()
        for _, _, name in get_datasources():
            try:
                schedule.removePeriodicEvent(name)
            except KeyError:
                # A newly added event may not exist, ignore exception.
                pass

    def _email_callback(self, fileobj):
        try:
            email = parse_mail(fileobj)
            msg = get_message(email)

            if not msg:
                return

            txt = colourise(msg.for_irc())

            # Simple flood/duplicate detection
            if txt in self.last_n_messages:
                return
            self.last_n_messages.insert(0, txt)
            self.last_n_messages = self.last_n_messages[:20]

            for channel in self.irc.state.channels:
                regex = self.registryValue('package_regex', channel) or 'a^'
                if re.search(regex, msg.package):
                    ircmsg = supybot.ircmsgs.privmsg(channel, txt)
                    self.irc.queueMsg(ircmsg)

        except:
            log.exception('Uncaught exception')

    def _topic_callback(self):
        self.topic_lock.acquire()

        sections = {
            lambda: len(TestingRCBugs().get_bugs()): 'RC bug count:',
            NewQueue().get_size: 'NEW queue:',
            RmQueue().get_size: 'RM queue:',
        }

        try:
            values = {}
            for callback, prefix in sections.iteritems():
                values[callback] = callback()

            for channel in self.irc.state.channels:
                new_topic = topic = self.irc.state.getTopic(channel)

                for callback, prefix in sections.iteritems():
                    if values[callback]:
                        new_topic = rewrite_topic(new_topic, prefix, values[callback])

                if topic != new_topic:
                    log.info("Queueing change of topic in #%s to '%s'" % (channel, new_topic))
                    self.queued_topics[channel] = new_topic

                    event_name = '%s_topic' % channel
                    try:
                        schedule.removeEvent(event_name)
                    except KeyError:
                        pass
                    schedule.addEvent(lambda channel=channel: self._update_topic(channel),
                        time.time() + 60, event_name)
        finally:
            self.topic_lock.release()

    def _update_topic(self, channel):
        self.topic_lock.acquire()
        try:
            try:
                new_topic = self.queued_topics[channel]
                log.info("Changing topic in #%s to '%s'" % (channel, new_topic))
                self.irc.queueMsg(supybot.ircmsgs.topic(channel, new_topic))
            except KeyError:
                pass
        finally:
            self.topic_lock.release()

    def greeting(self, prefix, irc, msg, args):
        num_bugs = len(TestingRCBugs().get_bugs())
        if type(num_bugs) is int:
            advice = random.choice((
                'Why not go and fix one?',
                'Why not peek at the list and find one?',
                'Stop IRCing and fix one! :]',
                'You realise they don\'t fix themselves, right?',
                'How about fixing yourself some caffeine and then poking at the bug list?',
            ))
            txt = "%s %s! There are currently %d RC bugs in squeeze. %s Try !random." % \
                (prefix, msg.nick, num_bugs, advice)
        else:
            txt = "%s %s!" % (prefix, msg.name)
        irc.reply(txt, prefixNick=False)

    def morning(self, *args):
        self.greeting('Good morning,', *args)
    morning = wrap(morning)
    yawn = wrap(morning)
    wakeywakey = wrap(morning)

    def night(self, *args):
        self.greeting( 'Good night,', *args)
    night = wrap(night)
    nn = wrap(night)
    goodnight = wrap(night)

    def sup(self, *args):
        self.greeting("'sup", *args)
    sup = wrap(sup)
    lo = wrap(sup)

    def rc(self, irc, msg, args):
        num_bugs = len(TestingRCBugs().get_bugs())
        if type(num_bugs) is int:
            irc.reply("There are %d release-critical bugs in the testing distribution. " \
                "See http://bts.turmzimmer.net/details.php?bydist=squeeze&igncontrib=on&ignnonfree=on" % num_bugs)
        else:
            irc.reply("No data at this time.")
    rc = wrap(rc)
    bugs = wrap(rc)

    def randombug(self, irc, msg, args):
        bug = random.choice(list(TestingRCBugs().get_bugs()))
        msg = "Your randomly chosen squeeze RC bug is: %s. Happy bugfixing!" % bug_synopsis(str(bug)).for_irc()
        irc.reply(colourise(msg))
    randombug = wrap(randombug)
    random = wrap(randombug)

    def update(self, irc, msg, args):
        if not ircdb.checkCapability(msg.prefix, 'owner'):
            irc.reply("You are not authorised to run this command.")
            return

        for klass, interval, name in get_datasources():
            klass().update()
            irc.reply("Updated %s." % name)
        self._topic_callback()
    update = wrap(update)

    def madison(self, irc, msg, args, package):
        try:
            lines = madison(package)
            if not lines:
                irc.reply('Did not get a response -- is "%s" a valid package?' % package)
                return

            field_styles = ('package', 'version', 'distribution', 'section')
            for line in lines:
                out = []
                fields = line.strip().split('|', len(field_styles))
                for style, data in zip(field_styles, fields):
                    out.append('[%s]%s' % (style, data))
                irc.reply(colourise('[reset]|'.join(out)), prefixNick=False)
        except Exception, e:
            irc.reply("Error: %s" % e.message)
    madison = wrap(madison, ['text'])

    def bug(self, irc, msg, args, bug_string):
        try:
            msg = bug_synopsis(bug_string)
            if msg:
                irc.reply(colourise(msg.for_irc()), prefixNick=False)
        except ValueError:
            irc.reply('Could not parse bug number')
        except Exception, e:
            irc.reply("Error: %s" % e.message)

    bug = wrap(bug, ['text'])

    def get_pool_url(self, package):
        if package.startswith('lib'):
            return (package[:4], package)
        else:
            return (package[:1], package)

    def _maintainer(self, irc, msg, args, items):
        for package in items:
            info = Maintainer().get_maintainer(package)
            if info:
                display_name = format_email_address("%s <%s>" % (info['name'], info['email']), max_domain=18)

                login = info['email']
                if login.endswith('@debian.org'):
                    login = login.replace('@debian.org', '')

                msg = "[desc]Maintainer for[reset] [package]%s[reset] [desc]is[reset] [by]%s[reset]: " % (package, display_name)
                msg += "[url]http://qa.debian.org/developer.php?login=%s[/url]" % login
            else:
                msg = 'Unknown source package "%s"' % package

            irc.reply(colourise(msg), prefixNick=False)
    maintainer = wrap(_maintainer, [many('anything')])
    maint = wrap(_maintainer, [many('anything')])
    who_maintains = wrap(_maintainer, [many('anything')])

    def _qa(self, irc, msg, args, items):
        for package in items:
            url = "http://packages.qa.debian.org/%s/%s.html" % self.get_pool_url(package)
            msg = "[desc]QA page for[reset] [package]%s[reset]: [url]%s[/url]" % (package, url)
            irc.reply(colourise(msg), prefixNick=False)
    qa = wrap(_qa, [many('anything')])
    overview = wrap(_qa, [many('anything')])
    package = wrap(_qa, [many('anything')])
    pkg = wrap(_qa, [many('anything')])
    srcpkg = wrap(_qa, [many('anything')])

    def _changelog(self, irc, msg, args, items):
        for package in items:
            url = "http://packages.debian.org/changelogs/pool/main/%s/%s/current/changelog" % self.get_pool_url(package)
            msg = "[desc]debian/changelog for[reset] [package]%s[reset]: [url]%s[/url]" % (package, url)
            irc.reply(colourise(msg), prefixNick=False)
    changelog = wrap(_changelog, [many('anything')])
    changes = wrap(_changelog, [many('anything')])

    def _copyright(self, irc, msg, args, items):
        for package in items:
            url = "http://packages.debian.org/changelogs/pool/main/%s/%s/current/copyright" % self.get_pool_url(package)
            msg = "[desc]debian/copyright for[reset] [package]%s[reset]: [url]%s[/url]" % (package, url)
            irc.reply(colourise(msg), prefixNick=False)
    copyright = wrap(_copyright, [many('anything')])

    def _buggraph(self, irc, msg, args, items):
        for package in items:
            msg = "[desc]Bug graph for[reset] [package]%s[reset]: [url]http://people.debian.org/~glandium/bts/%s/%s.png[/url]" % \
                (package, package[0], package)
            irc.reply(colourise(msg), prefixNick=False)
    buggraph = wrap(_buggraph, [many('anything')])
    bug_graph = wrap(_buggraph, [many('anything')])

    def _buildd(self, irc, msg, args, items):
        for package in items:
            msg = "[desc]buildd status for[reset] [package]%s[reset]: [url]http://buildd.debian.org/pkg.cgi?pkg=%s[/url]" % \
                (package, package)
            irc.reply(colourise(msg), prefixNick=False)
    buildd = wrap(_buildd, [many('anything')])

    def _buildde(self, irc, msg, args, items):
        for package in items:
            msg = "[desc]experimental/backports.org buildd status for[reset] [package]%s[reset]: [url]http://experimental.ftbfs.de/build.php?pkg=%s[/url]" % \
                (package, package)
            irc.reply(colourise(msg), prefixNick=False)
    buildde = wrap(_buildde, [many('anything')])
    builddb = wrap(_buildde, [many('anything')])
    experimental = wrap(_buildde, [many('anything')])
    backports = wrap(_buildde, [many('anything')])

    def _popcon(self, irc, msg, args, package):
        try:
            msg = popcon(package)
            if msg:
                irc.reply(colourise(msg.for_irc()), prefixNick=False)
        except Exception, e:
            irc.reply("Error: unable to obtain popcon data for %s" % package)
    popcon = wrap(_popcon, ['text'])

    def _testing(self, irc, msg, args, items):
        for package in items:
            msg = "[desc]Testing migration status for[reset] [package]%s[reset]: [url]http://release.debian.org/migration/testing.pl?package=%s[/url]" % \
                (package, package)
            irc.reply(colourise(msg), prefixNick=False)
    testing = wrap(_testing, [many('anything')])
    migration = wrap(_testing, [many('anything')])

    def _dehs(self, irc, msg, args, items):
        for package in items:
            msg = "[desc]Debian External Health Status for[reset] [package]%s[reset]: [url]http://dehs.alioth.debian.org/report.php?package=%s[/url]" % \
                (package, urllib.quote(package))
            irc.reply(colourise(msg), prefixNick=False)
    dehs = wrap(_dehs, [many('anything')])
    health = wrap(_dehs, [many('anything')])

    def _swirl(self, irc, msg, args):
        swirl = [
            "  [brightred] ,''`.[reset]",
            "  [brightred]: :' :[reset]           [b]Debian GNU/Linux[/b]",
            "  [brightred]`. `' [reset]           [url]http://www.debian.org/[/url]",
            "  [brightred]  `-  [reset]",
        ]
        for line in swirl:
            irc.reply(colourise(line), prefixNick=False)
    swirl = wrap(_swirl)
    debian = wrap(_swirl)

    def _pas(self, irc, msg, args):
        line = "[desc]Packages-arch-specific[reset]: [url]http://cvs.debian.org/srcdep/Packages-arch-specific?root=dak&view=auto[/url]"
        irc.reply(colourise(line))
    pas = wrap(_pas)
    packages_arch_specific = wrap(_pas)
    not_for_us = wrap(_pas)
    nfu = wrap(_pas)

    def _new(self, irc, msg, args):
        line = "[desc]NEW queue is[reset]: [url]%s[/url]. [desc]Current size is:[reset] %d" % \
            ("http://ftp-master.debian.org/new.html", NewQueue().get_size())
        irc.reply(colourise(line))
    new = wrap(_new)
    new_queue = wrap(_new)
    newqueue = wrap(_new)

Class = DebianDevelChanges
