import basetest
import unittest

import utils


class UtilsTest(unittest.TestCase):
    def test_connected(self):
        """ Test if the database connection works """

        self.assertTrue(utils.database_connect().isOpen())

