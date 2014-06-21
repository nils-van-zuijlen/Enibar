
# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
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


"""
Database
========

You can use the DB class like that:

.. code-block:: python

    from database import Cursor


    with Cursor() as cursor:
        # Use your cursor here
        cursor.prepare(...)
"""


from PyQt5 import QtSql
import settings


class Cursor:
    # pylint: disable=too-few-public-methods
    """ Context manager to use the database """
    def __init__(self):
        self.database = None
        self.cursor = None

    def __enter__(self):
        self.database = QtSql.QSqlDatabase("QMYSQL")

        self.database.setHostName(settings.HOST)
        self.database.setUserName(settings.USERNAME)
        self.database.setPassword(settings.PASSWORD)
        self.database.setDatabaseName(settings.DBNAME)

        self.database.open()
        self.cursor = QtSql.QSqlQuery(self.database)

        return self.cursor

    def __exit__(self, type_, value, traceback):
        self.database.close()

