# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
#
# This file is part of Enibar.
#
# Enibar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Enibar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.


from PyQt5 import QtCore, QtWidgets
from database import Cursor
import api.users
import api.notes
import api.redis
import api.sde
import asyncio
import os
import sys
import traceback
import unittest
import signal

from unittest.runner import TextTestResult, TextTestRunner
from unittest.signals import registerResult


def getDescription(self, test):
    doc_first_line = test.shortDescription()
    if self.descriptions and doc_first_line:
        return doc_first_line
    else:
        return str(test)


def startTest(self, test):
    super(TextTestResult, self).startTest(test)


def addSuccess(self, test):
    super(TextTestResult, self).addSuccess(test)
    if self.showAll:
        self.stream.writeln("[ \033[01;32m OK \033[0m ] {}".format(self.getDescription(test)))


def addError(self, test, err):
    super(TextTestResult, self).addError(test, err)
    self.stream.writeln("[ \033[01;31mERROR \033[0m] {}".format(self.getDescription(test)))
    traceback.print_exception(*err)


def addFailure(self, test, err):
    super(TextTestResult, self).addFailure(test, err)
    # This is ugly.
    self.stream.writeln("[ \033[01;31mFAIL \033[0m] {}".format(self.failures[-1][-1].replace("\n", "\n       ").replace("AssertionError", "  AssertionError")[:-8]))


def addSkip(self, test, reason):
    super(TextTestResult, self).addSkip(test, reason)
    self.stream.writeln("[ \033[01;33mSKIP \033[0m] {}: {!r}".format(self.getDescription(test), reason))


def run(self, test):
    "Run the given test case or test suite."
    result = self._makeResult()
    registerResult(result)
    result.failfast = self.failfast
    result.buffer = self.buffer
    startTestRun = getattr(result, 'startTestRun', None)
    if startTestRun is not None:
        startTestRun()
    try:
        test(result)
    finally:
        stopTestRun = getattr(result, 'stopTestRun', None)
        if stopTestRun is not None:
            stopTestRun()

    return result


class BaseTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(api.redis.connect())
        self.loop.run_until_complete(asyncio.ensure_future(self.reset_redis()))

    def tearDown(self):
        if api.redis.connection:
            api.redis.connection.close()
            self.loop.run_until_complete(api.redis.connection.wait_closed())

    async def reset_redis(self):
        async with api.redis.connection.get() as redis:
            res = await redis.delete(api.sde.QUEUE_NAME)

    def _reset_db(self):
        tables = ["admins", "categories", "products", "price_description",
                  "notes", "prices", "transactions", "panels", "panel_content",
                  "scheduled_mails", "mail_models", "note_categories"]
        with Cursor() as cursor:
            for table in tables:
                cursor.exec_("DELETE FROM {}".format(table))
                cursor.exec_("ALTER TABLE {} AUTO_INCREMENT = 1".format(table))
        api.notes.rebuild_cache()

    def assertMyDictEqual(self, d1, d2, ignore=None):
        """ ignore is a list of keys to ignore but that should be there in d1
        """
        if ignore is None:
            self.assertEqual(d1, d2)
        else:
            for key, value in d1.items():
                if key not in ignore:
                    self.assertEqual(value, d2[key])

        for key in ignore:
            if key not in d1:
                raise self.failureException()

    def assertDictListEqual(self, l1, l2, ignore=None):
        """ ignore is a list of keys to ignore but that should be there in l1
        """
        if len(l1) != len(l2):
            raise self.failureException()

        for d1, d2 in zip(l1, l2):
            self.assertMyDictEqual(d1, d2, ignore=ignore)

    def add_note(self, nick, name=None, first_name=None, mail="test@pouette.fr",
            stats_inscription=True, mails_inscription=True):
        note = api.notes.add(nick,
            first_name or nick,
            name or nick,
            mail,
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            stats_inscription,
            mails_inscription
        )
        api.notes.rebuild_cache()
        return note

    def _count(self, db):
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM {}".format(db))
            if cursor.next():
                return cursor.record().value(0)

    def count_categories(self):
        """ Returns the number of categories currently in database """
        return self._count("categories")

    def count_transactions(self):
        """ Returns the number of transactions currently in database """
        return self._count("transactions")

    def count_descriptors(self):
        """ Returns the number of descriptions currently in database """
        return self._count("price_description")

    def count_prices(self):
        """ Returns the number of prices currently in database """
        return self._count("prices")

    def count_products(self):
        """ Returns the number of products currently in database """
        return self._count("products")

    def count_notes(self):
        """ Returns the number of notes currently in database """
        return self._count("notes")

    def count_panels(self):
        """ Returns the number of panels currently in database """
        return self._count("panels")

    def count_admins(self):
        """ Test helper, returns the number of admins currently in database """
        return self._count("admins")

    def count_note_categories(self):
        """ Returns the number of note_categories currently in database """
        return self._count("note_categories")


class BaseGuiTest(BaseTest):
    def setUp(self):
        super().setUp()
        api.redis.send_message = lambda x, y: [api.notes.rebuild_note_cache(note) for note in y]
        self.app = QtWidgets.QApplication(sys.argv)
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(30)

    def handle_timeout(self, _, __):
        self.app.quit()
        raise TimeoutError()

    def tearDown(self):
        super().tearDown()
        self.app.quit()
        self.app = None  # Need this to avoid X11 crash. It may cause segfault.

    def _reset_db(self):
        """ Reset the db but add an user that can do anything
        """
        super()._reset_db()
        api.users.add("azerty", "azerty")
        api.users.set_rights("azerty", {'manage_users': True,
                                        'manage_notes': True,
                                        'manage_products': True}
        )

    def connect(self):
        def connect_callback():
            auth_window = self.app.activeWindow()
            auth_window.pass_input.setText("azerty")
            auth_window.accept_button.click()
        QtCore.QTimer().singleShot(200, connect_callback)

    def get_items(self, qlist):
        return [qlist.item(i).text() for i in range(qlist.count())]

    def get_tree(self, qtree):
        tree = []

        def get_child(item, first=False):
            if item.childCount():
                if first:
                    return {tuple(item.text(i) for i in range(item.columnCount())): [get_child(item.child(j)) for j in range(item.childCount())]}
                return [{tuple(item.text(i) for i in range(item.columnCount())): get_child(item.child(j))} for j in range(item.childCount())]
            return {tuple(item.text(i) for i in range(item.columnCount())): []}
        for i in range(qtree.topLevelItemCount()):
            tree.append(get_child(qtree.topLevelItem(i), first=True))
        return tree


TextTestResult.getDescription = getDescription
TextTestResult.startTest = startTest
TextTestResult.addSuccess = addSuccess
TextTestResult.addError = addError
TextTestResult.addFailure = addFailure
TextTestResult.addSkip = addSkip
TextTestRunner.run = run

