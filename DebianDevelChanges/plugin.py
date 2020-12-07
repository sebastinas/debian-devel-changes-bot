#
#   Debian Changes Bot
#   Copyright (C) 2008 Chris Lamb <chris@chris-lamb.co.uk>
#   Copyright (C) 2015-2017 Sebastian Ramacher <sramacher@debian.org>
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
import urllib.parse
import supybot
import threading
import requests
import email.utils

from gi.repository import GObject
from pydbus import SystemBus
from supybot import ircdb, log, schedule
from supybot.commands import wrap, many

from DebianDevelChangesBot import NewDataSource, pseudo_packages
from DebianDevelChangesBot.mailparsers import get_message
from DebianDevelChangesBot.datasources import (
    TestingRCBugs,
    NewQueue,
    RmQueue,
    StableRCBugs,
    Dinstall,
    AptArchive,
    PseudoPackages,
)
from DebianDevelChangesBot.utils import (
    parse_mail,
    colourise,
    rewrite_topic,
    madison,
    format_email_address,
    popcon,
)
from DebianDevelChangesBot.utils.decoding import split_address
from DebianDevelChangesBot.utils.dbus import BTSDBusService


class DebianDevelChanges(supybot.callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        super().__init__(irc)
        self.irc = irc
        self.topic_lock = threading.Lock()

        self.mainloop = None
        self.mainloop_thread = None
        mainloop = GObject.MainLoop()
        if not mainloop.is_running():
            log.info("Starting Glib main loop")
            mainloop_thread = threading.Thread(
                target=mainloop.run, name="Glib maing loop"
            )
            mainloop_thread.start()
            self.mainloop_thread = mainloop_thread
            self.mainloop = mainloop

        self.requests_session = requests.Session()
        self.requests_session.verify = True

        self.queued_topics = {}
        self.last_n_messages = []

        # data sources
        pseudo_packages.pp = PseudoPackages(self.requests_session)
        self.pseudo_packages = pseudo_packages.pp
        self.stable_rc_bugs = StableRCBugs(self.requests_session)
        self.testing_rc_bugs = TestingRCBugs(self.requests_session)
        self.new_queue = NewQueue(self.requests_session)
        self.dinstall = Dinstall(self.requests_session)
        self.rm_queue = RmQueue(self.requests_session)
        self.apt_archive = AptArchive(
            self.registryValue("apt_configuration_directory"),
            self.registryValue("apt_cache_directory"),
        )
        self.data_sources = (
            self.pseudo_packages,
            self.stable_rc_bugs,
            self.testing_rc_bugs,
            self.new_queue,
            self.dinstall,
            self.rm_queue,
            self.apt_archive,
        )

        # Schedule datasource updates
        def wrapper(source):
            def implementation():
                try:
                    source.update()
                except Exception as e:
                    log.exception(f"Failed to update {source.NAME}: {e}")
                self._topic_callback()

            return implementation

        for source in self.data_sources:
            # schedule periodic events
            schedule.addPeriodicEvent(
                wrapper(source), source.INTERVAL, source.NAME, now=False
            )
            # and run them now once
            schedule.addEvent(wrapper(source), time.time() + 1)

        log.info("Starting D-Bus service")
        self.dbus_service = BTSDBusService(self._email_callback)
        self.dbus_bus = SystemBus()
        self.dbus_bus.publish(self.dbus_service.interface_name, self.dbus_service)
        self.dbus_service.start()

    def die(self):
        log.info("Stopping D-Bus service")
        self.dbus_service.stop()
        if self.mainloop is not None:
            log.info("Stopping Glib main loop")
            self.mainloop.quit()
            self.mainloop_thread.join(timeout=1.0)
            if self.mainloop_thread.is_alive():
                log.warn("Glib main loop thread is still alive.")

            self.mainloop = None
            self.mainloop_thread = None

        for source in self.data_sources:
            try:
                schedule.removePeriodicEvent(source.NAME)
            except KeyError:
                pass

        super().die()

    def _email_callback(self, fileobj):
        try:
            emailmsg = parse_mail(fileobj)
            msg = get_message(emailmsg, new_queue=self.new_queue)

            if not msg:
                return

            txt = colourise(msg.for_irc())

            # Simple flood/duplicate detection
            if txt in self.last_n_messages:
                return
            self.last_n_messages.insert(0, txt)
            self.last_n_messages = self.last_n_messages[:20]

            packages = [package.strip() for package in msg.package.split(",")]

            maintainer_info = None
            if hasattr(msg, "maintainer"):
                maintainer_info = (split_address(msg.maintainer),)
            else:
                maintainer_info = []
                for package in packages:
                    try:
                        maintainer_info.append(self.apt_archive.get_maintainer(package))
                    except NewDataSource.DataError as e:
                        log.info(f"Failed to query maintainer for {package}.")

            for channel in self.irc.state.channels:
                # match package or nothing by default
                package_regex = self.registryValue("package_regex", channel) or "a^"
                package_match = False
                for package in packages:
                    package_match = re.search(package_regex, package)
                    if package_match:
                        break

                maintainer_match = False
                maintainer_regex = self.registryValue("maintainer_regex", channel)
                if (
                    maintainer_regex
                    and maintainer_info is not None
                    and len(maintainer_info) >= 0
                ):
                    for mi in maintainer_info:
                        maintainer_match = re.search(maintainer_regex, mi["email"])
                        if maintainer_match:
                            break

                if not package_match and not maintainer_match:
                    continue

                distribution_regex = self.registryValue("distribution_regex", channel)

                if distribution_regex:
                    if not hasattr(msg, "distribution"):
                        # If this channel has a distribution regex, don't
                        # bother continuing unless the message actually has a
                        # distribution. This filters security messages, etc.
                        continue

                    if not re.search(distribution_regex, msg.distribution):
                        # Distribution doesn't match regex; don't send this
                        # message.
                        continue

                send_privmsg = self.registryValue("send_privmsg", channel)
                # Send NOTICE per default and if 'send_privmsg' is set for the
                # channel, send PRIVMSG instead.
                if send_privmsg:
                    ircmsg = supybot.ircmsgs.privmsg(channel, txt)
                else:
                    ircmsg = supybot.ircmsgs.notice(channel, txt)

                self.irc.queueMsg(ircmsg)

        except Exception as e:
            log.exception("Uncaught exception: %s " % e)

    def _topic_callback(self):
        sections = {
            self.testing_rc_bugs.get_number_bugs: "RC bug count",
            self.stable_rc_bugs.get_number_bugs: "stable RC bug count",
            self.new_queue.get_size: "NEW queue",
            self.new_queue.get_backports_size: "backports NEW queue",
            self.rm_queue.get_size: "RM queue",
            self.dinstall.get_status: "dinstall",
        }

        channels = set()
        with self.topic_lock:
            values = {}
            for callback, prefix in sections.items():
                new_value = callback()
                if new_value is not None:
                    values[prefix] = new_value

            for channel in self.irc.state.channels:
                new_topic = topic = self.irc.state.getTopic(channel)

                for prefix, value in values.items():
                    new_topic = rewrite_topic(new_topic, prefix, value)

                if topic != new_topic:
                    self.queued_topics[channel] = new_topic

                    if channel not in channels:
                        log.info(
                            "Queueing change of topic in #%s to '%s'"
                            % (channel, new_topic)
                        )
                        channels.add(channel)

        for channel in channels:
            event_name = f"{channel}_topic"
            try:
                schedule.removeEvent(event_name)
            except KeyError:
                pass

            def update_topic(channel=channel):
                self._update_topic(channel)

            schedule.addEvent(update_topic, time.time() + 60, event_name)

    def _update_topic(self, channel):
        with self.topic_lock:
            try:
                new_topic = self.queued_topics[channel]
                log.info(f"Changing topic in #{channel} to '{new_topic}'")
                self.irc.queueMsg(supybot.ircmsgs.topic(channel, new_topic))
            except KeyError:
                pass

    def rc(self, irc, msg, args):
        """Link to UDD RC bug overview."""
        num_bugs = self.testing_rc_bugs.get_number_bugs()
        if type(num_bugs) is int:
            irc.reply(
                "There are %d release-critical bugs in the testing distribution. "
                "See https://udd.debian.org/bugs.cgi?release=bullseye&notmain=ign&merged=ign&rc=1"
                % num_bugs
            )
        else:
            irc.reply("No data at this time.")

    rc = wrap(rc)
    bugs = wrap(rc)

    def update(self, irc, msg, args):
        """Trigger an update."""
        if not ircdb.checkCapability(msg.prefix, "owner"):
            irc.reply("You are not authorised to run this command.")
            return

        for source in self.data_sources:
            source.update()
            irc.reply("Updated %s." % source.NAME)
        self._topic_callback()

    update = wrap(update)

    def madison(self, irc, msg, args, package):
        """List packages."""
        try:
            lines = madison(package)
            if not lines:
                irc.reply(
                    'Did not get a response -- is "%s" a valid package?' % package
                )
                return

            field_styles = ("package", "version", "distribution", "section")
            for line in lines:
                out = []
                fields = line.strip().split("|", len(field_styles))
                for style, data in zip(field_styles, fields):
                    out.append(f"[{style}]{data}")
                irc.reply(colourise("[reset]|".join(out)), prefixNick=False)
        except Exception as e:
            irc.reply("Error: %s" % e.message)

    madison = wrap(madison, ["text"])

    def get_pool_url(self, package):
        if package.startswith("lib"):
            return (package[:4], package)
        else:
            return (package[:1], package)

    def _maintainer(self, irc, msg, args, items):
        """Get maintainer for package."""
        for package in items:
            info = self.apt_archive.get_maintainer(package)
            if info:
                display_name = format_email_address(
                    "{} <{}>".format(info["name"], info["email"]), max_domain=18
                )

                login = info["email"]
                if login.endswith("@debian.org"):
                    login = login.replace("@debian.org", "")

                msg = (
                    "[desc]Maintainer for[reset] [package]%s[reset] [desc]is[reset] [by]%s[reset]: "
                    % (package, display_name)
                )
                msg += "[url]https://qa.debian.org/developer.php?login=%s[/url]" % login
            else:
                msg = 'Unknown source package "%s"' % package

            irc.reply(colourise(msg), prefixNick=False)

    maintainer = wrap(_maintainer, [many("anything")])
    maint = wrap(_maintainer, [many("anything")])
    who_maintains = wrap(_maintainer, [many("anything")])

    def _qa(self, irc, msg, args, items):
        """Get link to QA page."""
        for package in items:
            url = "https://packages.qa.debian.org/%s/%s.html" % self.get_pool_url(
                package
            )
            msg = "[desc]QA page for[reset] [package]{}[reset]: [url]{}[/url]".format(
                package,
                url,
            )
            irc.reply(colourise(msg), prefixNick=False)

    qa = wrap(_qa, [many("anything")])
    overview = wrap(_qa, [many("anything")])
    package = wrap(_qa, [many("anything")])
    pkg = wrap(_qa, [many("anything")])
    srcpkg = wrap(_qa, [many("anything")])

    def _changelog(self, irc, msg, args, items):
        """Get link to changelog."""
        for package in items:
            url = (
                "https://packages.debian.org/changelogs/pool/main/%s/%s/current/changelog"
                % self.get_pool_url(package)
            )
            msg = (
                "[desc]debian/changelog for[reset] [package]%s[reset]: [url]%s[/url]"
                % (package, url)
            )
            irc.reply(colourise(msg), prefixNick=False)

    changelog = wrap(_changelog, [many("anything")])
    changes = wrap(_changelog, [many("anything")])

    def _copyright(self, irc, msg, args, items):
        """Link to copyright files."""
        for package in items:
            url = (
                "https://packages.debian.org/changelogs/pool/main/%s/%s/current/copyright"
                % self.get_pool_url(package)
            )
            msg = (
                "[desc]debian/copyright for[reset] [package]%s[reset]: [url]%s[/url]"
                % (package, url)
            )
            irc.reply(colourise(msg), prefixNick=False)

    copyright = wrap(_copyright, [many("anything")])

    def _buggraph(self, irc, msg, args, items):
        """Link to bug graph."""
        for package in items:
            msg = (
                "[desc]Bug graph for[reset] [package]%s[reset]: [url]https://qa.debian.org/data/bts/graphs/%s/%s.png[/url]"
                % (package, package[0], package)
            )
            irc.reply(colourise(msg), prefixNick=False)

    buggraph = wrap(_buggraph, [many("anything")])
    bug_graph = wrap(_buggraph, [many("anything")])

    def _buildd(self, irc, msg, args, items):
        """Link to buildd page."""
        for package in items:
            msg = (
                "[desc]buildd status for[reset] [package]%s[reset]: [url]https://buildd.debian.org/pkg.cgi?pkg=%s[/url]"
                % (package, package)
            )
            irc.reply(colourise(msg), prefixNick=False)

    buildd = wrap(_buildd, [many("anything")])

    def _popcon(self, irc, msg, args, package):
        """Get popcon data."""
        try:
            msg = popcon(package, self.requests_session)
            if msg:
                irc.reply(colourise(msg.for_irc()), prefixNick=False)
        except Exception as e:
            irc.reply("Error: unable to obtain popcon data for %s" % package)

    popcon = wrap(_popcon, ["text"])

    def _testing(self, irc, msg, args, items):
        """Check testing migration status."""
        for package in items:
            msg = (
                "[desc]Testing migration status for[reset] [package]%s[reset]: [url]https://qa.debian.org/excuses.php?package=%s[/url]"
                % (package, package)
            )
            irc.reply(colourise(msg), prefixNick=False)

    testing = wrap(_testing, [many("anything")])
    migration = wrap(_testing, [many("anything")])

    def _new(self, irc, msg, args):
        """Link to NEW queue."""
        line = (
            "[desc]NEW queue is[reset]: [url]%s[/url]. [desc]Current size is:[reset] %d"
            % ("https://ftp-master.debian.org/new.html", self.new_queue.get_size())
        )
        irc.reply(colourise(line))

    new = wrap(_new)
    new_queue = wrap(_new)
    newqueue = wrap(_new)


Class = DebianDevelChanges
