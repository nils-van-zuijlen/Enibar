# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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
from pyvirtualdisplay import Display
import api.users
import api.notes
import os
import subprocess
import sys
import traceback
import unittest
import warnings

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
    run = result.testsRun

    return result


class BaseTest(unittest.TestCase):
    def _reset_db(self):
        tables = ["admins", "categories", "products", "price_description",
                  "notes", "prices", "transactions", "panels", "panel_content"]
        with Cursor() as cursor:
            for table in tables:
                cursor.exec_("DELETE FROM {}".format(table))
                cursor.exec_("ALTER TABLE {} AUTO_INCREMENT = 1".format(table))
        api.notes.rebuild_cache()

    def assertMyDictEqual(self, d1, d2, ignore=None):
        """ ignore is a list of keys to ignore but that should be there in d1
        """
        if ignore is None:
            self.assertEqual(d1 == d2)
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

    def add_note(self, nick, name="test1", first_name="test1"):
        return api.notes.add(nick,
            first_name,
            name,
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )


class BaseGuiTest(BaseTest):
    def setUp(self):
        if int(os.environ['USE_VD']):
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        self.app = QtWidgets.QApplication(sys.argv)

    def tearDown(self):
        self.app = None  # Need this to avoid X11 crash. It may cause segfault.
        if int(os.environ['USE_VD']):
            self.display.stop()

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
        timer = QtCore.QTimer().singleShot(200, connect_callback)


TextTestResult.getDescription = getDescription
TextTestResult.startTest = startTest
TextTestResult.addSuccess = addSuccess
TextTestResult.addError = addError
TextTestResult.addFailure = addFailure
TextTestResult.addSkip = addSkip
TextTestRunner.run = run

