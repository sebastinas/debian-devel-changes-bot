#!/usr/bin/env python
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

import unittest

from io import BytesIO
from DebianDevelChangesBot.utils import parse_mail


class TestUtilsParseMail(unittest.TestCase):
    def testSimple(self):
        f = BytesIO(
            b"""\
From: Chris Lamb <chris@chris-lamb.co.uk>
Subject: This is the subject

Simple message body"""
        )

        headers, body = parse_mail(f)

        self.assertEqual(headers['From'], "Chris Lamb <chris@chris-lamb.co.uk>")
        self.assertEqual(headers['Subject'], "This is the subject")
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0], "Simple message body")

        self.assertEqual(type(headers['From']), str)
        self.assertEqual(type(headers['Subject']), str)
        self.assertEqual(type(body[0]), str)

    def testLongSubject(self):
        f = BytesIO(
            b"""\
From: Chris Lamb <chris@chris-lamb.co.uk>
Subject: Bug#123456: marked as done (pinafore: Inertial couplings may
 exceed tolerance when docking)

Simple message body"""
        )

        headers, body = parse_mail(f)

        self.assertEqual(
            headers['Subject'],
            "Bug#123456: marked as done "
            "(pinafore: Inertial couplings may exceed tolerance when docking)",
        )

    def testLongLine(self):
        f = BytesIO(
            b"""\
Subject: Subject

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
"""
        )

        headers, body = parse_mail(f)
        self.assertEqual(body[0], ('A' * 73) + ('B' * 73) + ('C' * 73))

    def testNotLongLine(self):
        f = BytesIO(
            b"""\
Subject: Subject

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
"""
        )

        headers, body = parse_mail(f)
        self.assertNotEqual(body, [('A' * 73) + ('B' * 73) + ('C' * 73)])

    def testSpaceAtEndOfLine(self):
        f = BytesIO(
            b"""\
Subject: Subject

Description:=20
"""
        )

        headers, body = parse_mail(f)
        self.assertEqual(body, ['Description: '])

    def testUnicodeHeader(self):
        f = BytesIO(
            b"""\
From: Gon=C3=A9ri Le Bouder

Message body
"""
        )

        headers, body = parse_mail(f)
        self.assertEqual(headers['From'], "Gonéri Le Bouder")
        self.assertEqual(body, ['Message body'])

    def testUnicodeBody(self):
        f = BytesIO(
            b"""\
Subject: Subject line

Gon=C3=A9ri Le Bouder
"""
        )
        headers, body = parse_mail(f)
        self.assertEqual(headers['Subject'], 'Subject line')
        self.assertEqual(body, ["Gon=C3=A9ri Le Bouder"])

    def testUtf8Header(self):
        f = BytesIO(
            b"""\
From: Sebastian =?UTF-8?Q?Dr=C3=B6ge?=

Message body"""
        )

        headers, body = parse_mail(f)
        self.assertEqual(headers['From'], "Sebastian Dröge")
        self.assertEqual(body, ['Message body'])

    def testUtf8Header2(self):
        f = BytesIO(
            b"""\
From: marc.poulhies@imag.fr (Marc =?ISO-8859-1?Q?Poulhi=E8s?=)

Message body"""
        )
        headers, body = parse_mail(f)
        self.assertEqual(headers['From'], "marc.poulhies@imag.fr (Marc Poulhiès)")
        self.assertEqual(body, ['Message body'])

    def testMultipart(self):
        f = BytesIO(
            b"""\
From: Mohammed Sameer <msameer@foolab.org>
To: Cristian Greco <cgreco@cs.unibo.it>
Cc: 402462@bugs.debian.org
Content-Type: multipart/signed; micalg=pgp-sha1;
	protocol="application/pgp-signature"; boundary="JlJsEFsx9RQyiX4C"
Content-Disposition: inline


--JlJsEFsx9RQyiX4C
Content-Type: text/plain; charset=utf-8
Content-Disposition: inline
Content-Transfer-Encoding: quoted-printable

On Sat, Apr 19, 2008 at 04:45:42PM +0200, Cristian Greco wrote:
> owner 402462 !
> thanks
>=20
> I'll work on this package, Mohammed Sameer agree with me because he is to=
o busy
> now.

Acknowledged.

--=20
GPG-Key: 0xA3FD0DF7 - 9F73 032E EAC9 F7AD 951F  280E CB66 8E29 A3FD 0DF7
Debian User and Developer.
Homepage: www.foolab.org

--JlJsEFsx9RQyiX4C
Content-Type: application/pgp-signature; name="signature.asc"
Content-Description: Digital signature
Content-Disposition: inline

-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.6 (GNU/Linux)

iD8DBQFICoPwy2aOKaP9DfcRAn7xAJ486L4EWnH/nL176FF4yZSoT2xKEACeNZX4
orkuFNMGzF2Qx9fiQRLWemE=
=ivv9
-----END PGP SIGNATURE-----

--JlJsEFsx9RQyiX4C--
"""
        )

        headers, body = parse_mail(f)
        self.assertTrue("Acknowledged." in body)


if __name__ == "__main__":
    unittest.main()
