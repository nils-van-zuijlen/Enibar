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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.


"""

Settings
========

Database
^^^^^^^^

.. glossary::
    :sorted:

    HOST

            **Default value:** ``localhost``

            Adress of the mysql server.

    USERNAME

            **Default value:** ``root``

            Username of an user on the mysql server. He must be granted with
            all rights.

    PASSWORD

            **Default value:** ``[empty]``

            Password for the user.

    DBNAME

            **Default value:** ``enibar``

            The name of the database used by the software.

    MINORS_COLOR

        **Default value:** ``QtGui.QColor(255, 192, 203)``

        The color of the minors in the notes list

    OVERDRAFT_COLOR

        **Default value:** ``QtCore.Qt.red``

        The color of notes below 0€
"""

from PyQt5 import QtGui, QtCore


HOST = ""
USERNAME = "root"
PASSWORD = ""
DBNAME = "enibar"

MINORS_COLOR = QtGui.QColor(255, 192, 203)
OVERDRAFT_COLOR = QtCore.Qt.red
