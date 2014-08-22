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
import sys
import settings


class Database:
    database = None
    # pylint: disable=too-few-public-methods
    """ Context manager to use the database """
    def __init__(self):
        if Database.database is None:
            Database.database = QtSql.QSqlDatabase("QMYSQL")

            Database.database.setHostName(settings.HOST)
            Database.database.setUserName(settings.USERNAME)
            Database.database.setPassword(settings.PASSWORD)
            Database.database.setDatabaseName(settings.DBNAME)
            if not Database.database.open():
                print("Can't join database")
                sys.exit(1)
            cursor = SqlQuery(self.database)
            cursor.exec("SET AUTOCOMMIT=0")
            cursor.exec("ST innodb_flush_log_at_trx_commit=0")

    def __enter__(self):
        return self.database

    def __exit__(self, type_, value, traceback):
        pass


class Cursor(Database):
    # pylint: disable=too-few-public-methods
    """ Context manager to use the cursor """
    def __init__(self):
        super().__init__()
        self.cursor = None

    def __enter__(self):
        super().__enter__()
        self.cursor = SqlQuery(self.database)
        return self.cursor

    def __exit__(self, type_, value, traceback):
        self.database.commit()


class SqlQuery(QtSql.QSqlQuery):
    # pylint: disable=too-few-public-methods,invalid-name
    """ Wrapper around QtSql.QSqlQuery to add multiple binding funcion """
    def bindValues(self, kwargs):
        """ Bind multiple values to the query

        :param dict **kwargs: A dict formed like that: {":placeholder": value, }

        :return None:
        """

        for key, value in kwargs.items():
            self.bindValue(key, value)

