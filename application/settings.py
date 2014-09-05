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

    DEBUG
            **Default value** ``False``

            If True, the password will never be asked

    ECOCUP_PRICE
            **Default value** ``1.0``

            The price of an ecocup

    IMG_BASE_DIR
            **Default value** ``img/``

            The base dir for all images

    AGIO_THRESHOLD
            **Default value** ``14``

            Period after which agio are applied if a note stay in the red in
            days.

    AGIO_EVERY
            **Default value** ``7``

            Delay between two agio strike in days.

    AGIO_PERCENT
            **Default value** ``5.0``

            Agio value

"""


HOST = ""
USERNAME = "root"
PASSWORD = ""
DBNAME = "enibar"

DEBUG = False
ECOCUP_PRICE = 1.0
IMG_BASE_DIR = "img/"

AGIO_THRESHOLD = 14
AGIO_EVERY = 7
AGIO_PERCENT = 5.0
