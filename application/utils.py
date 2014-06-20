"""
Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>

This file is part of Enibar.

Enibar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Enibar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

"""


from PyQt5 import QtSql
import settings


def database_connect():
    """
    Open a connection to database.

    :return: Database object.
    :rtype: `QSqlDatabase`
    """

    database = QtSql.QSqlDatabase("QMYSQL")

    database.setHostName(settings.HOST)
    database.setUserName(settings.USERNAME)
    database.setPassword(settings.PASSWORD)
    database.setDatabaseName(settings.DBNAME)

    database.open()

    return database
