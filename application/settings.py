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

            **Default value:** ``127.0.0.1``

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


Ecocups
^^^^^^^

.. glossary::
    :sorted:

    ECOCUP_PRICE
            **Default value** ``1.0``

            The price of an ecocup.

    ECOCUP_NAME
            **Default value** ``Ecocup``

            The name used to identify ecocup. This name will be displayed in
            the history and other products list.

    ECOCUP_CATEGORY
            **Default value** ``Bar``

            Category name of ecocup. Used to display category name on ecocup
            transaction.

    ECOCUP_PRICE_TYPES
            **Default value** ``{'take': "Achat", 'repay': "Remboursement"}``

            Prices name displayed for ecocup in take and repay transation.


Agios
^^^^^

.. glossary::
    :sorted:

    AGIO_THRESHOLD
            **Default value** ``14``

            Time lapse after which agio are applied if a note stay in the red\
            (in days).

    AGIO_EVERY
            **Default value** ``7``

            Delay between two agio strike in days.

    AGIO_PERCENT
            **Default value** ``5.0``

            Agio value.

Mail
^^^^

..glossary::
    :sorter:


    SMTP_SERVER_ADDR
            **Default value** ``smtp.enib.fr``

            Smtp server used to send mail

    SMTP_SERVER_PORT
            **Default value** ``25``

            Smtp port used to connect to server

Other
^^^^^

.. glossary::
    :sorted:

    DEBUG
            **Default value** ``False``

            If True, the password will never be asked

    ASK_VALIDATION_VALIDATE
            **Default value** ``True``

            If True, a confirmation will be asked when clicking on « Valider »
            on the MainWindow.

    ASK_VALIDATION_REFILL
            **Default value** ``True``

            If True, a confirmation will be asked when refilling a note.

    MAX_HISTORY
            **Default value** ``5``

            Defines the maximum number of history lines printed on the
            MainWindow.

    IMG_BASE_DIR
            **Default value** ``img/``

            The base dir for all images.

    ALCOHOL_MAJORATION
            **Default value** ``0.0``

            Majoration on alcohols

"""


IMG_BASE_DIR = "img/"
DEBUG = False
ASK_VALIDATION_VALIDATE = True
ASK_VALIDATION_REFILL = True
MAX_HISTORY = 5
ALCOHOL_MAJORATION = 5

#
# Database settings
#

HOST = "127.0.0.1"
USERNAME = "root"
PASSWORD = ""
DBNAME = "enibar"


#
# Agio settings
#

AGIO_THRESHOLD = 14
AGIO_EVERY = 7
AGIO_PERCENT = 5.0


#
# Ecocup settings
#

ECOCUP_PRICE = 1.0
ECOCUP_CATEGORY = "Bar"
ECOCUP_PRICE_TYPES = {'take': "Achat", 'repay': "Remboursement"}
# Note that changing the following settings will break ecocup count.
# Do not change it unless you know what you are doing.
ECOCUP_NAME = "Ecocup"


#
# MAIL
#
SMTP_SERVER_ADDR = 'smtp.enib.fr'
SMTP_SERVER_PORT = 25
