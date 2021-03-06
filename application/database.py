# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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


from PyQt5 import QtSql, QtWidgets
import asyncio
import rapi
import os
import settings
import sys


class Database:
    """ Context manager to use the database """
    database = None

    def __init__(self):
        self.connect()

    def __enter__(self):
        return self.database

    def __exit__(self, type_, value, traceback):
        pass

    def connect(self):
        """ Connect to the database and set some parameters.
        """
        if Database.database is None:
            Database.database = QtSql.QSqlDatabase("QPSQL")
            Database.database.setHostName(os.environ.get(
                "DATABASE_HOST",
                settings.DB_HOST
            ))
            Database.database.setPort(int(os.environ.get(
                "DATABASE_PORT",
                settings.DB_PORT,
            )))
            Database.database.setUserName(os.environ.get(
                "DATABASE_USER",
                settings.USERNAME
            ))
            Database.database.setPassword(os.environ.get(
                "DATABASE_PASSWORD",
                settings.PASSWORD
            ))
            Database.database.setDatabaseName(os.environ.get(
                "DATABASE_NAME",
                settings.DBNAME
            ))
            if not Database.database.open():
                if rapi.utils.check_x11():
                    # We need this to create an app before opening a window.
                    import gui.utils
                    self.tmp = QtWidgets.QApplication(sys.argv)
                    gui.utils.error("Error", "Can't join database")
                print("Can't join database")
                sys.exit(1)


class Cursor(Database):
    """ Context manager to use the cursor """
    def __init__(self):
        super().__init__()
        self.cursor = None

    def __enter__(self):
        super().__enter__()
        self.cursor = SqlQuery(self.database)
        return self.cursor

    if settings.DEBUG:
        def exec_(self, *args):
            ret = super().exec_(*args)
            if not ret:
                print(self.lastError().text())
            return ret

        def execBatch(self, *args):
            ret = super().execBatch(*args)
            if not ret:
                print(self.lastError().text())
            return ret

        def prepare(self, query):
            ret = super().prepare(query)
            if not ret:
                print(self.lastError().text())
            return ret


class SqlQuery(QtSql.QSqlQuery):
    """ Wrapper around QtSql.QSqlQuery to add multiple binding funcion """
    def bindValues(self, kwargs):
        """ Bind multiple values to the query

        :param dict \*\*kwargs: A dict formed like that: {":placeholder": value, }

        :return None:
        """

        for key, value in kwargs.items():
            self.bindValue(key, value)

    def indexOf(self, name):
        return self.record().indexOf(name)

    if settings.DEBUG:
        def exec_(self, *args):
            ret = super().exec_(*args)
            if not ret:
                print(self.lastError().text())
            return ret

        def execBatch(self, *args):
            ret = super().execBatch(*args)
            if not ret:
                print(self.lastError().text())
            return ret

        def prepare(self, query):
            ret = super().prepare(query)
            if not ret:
                print(self.lastError().text())
            return ret


async def ping_sql(app):
    while True:
        await asyncio.sleep(10)
        with Cursor() as cursor:
            cursor.prepare("SELECT 1")
            cursor.exec_()


# Open the database connection as soon as possible
Database()
