from database import Cursor
import os
import traceback
import unittest
import warnings
import subprocess

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


TextTestResult.getDescription = getDescription
TextTestResult.startTest = startTest
TextTestResult.addSuccess = addSuccess
TextTestResult.addError = addError
TextTestResult.addFailure = addFailure
TextTestResult.addSkip = addSkip
TextTestRunner.run = run

