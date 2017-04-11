# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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

    DB_HOST

            **Default value:** ``127.0.0.1``

            Adress of the postgresql server.

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

Redis
^^^^^
.. glossary::
    :sorted:

    REDIS_HOST
        **Default value:** ``127.0.0.1``

        Adress of the redis server.

    REDIS_PASSWORD
        **Default value:** ``None``

        The password of the redis instance if it requires one, None otherwise.


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
    :sorted:


    SMTP_SERVER_ADDR
            **Default value** ``smtp.enib.fr``

            Smtp server used to send mail

    SMTP_SERVER_PORT
            **Default value** ``25``

            Smtp port used to connect to server

Students website
^^^^^^^^^^^^^^^^

..glossary:
    :sorted:


    WEB_URL
        **Default value** ``http://enib.net/enibar/api/``

    AUTH_SDE_TOKEN
        **Default value** ``changeme``
        You NEED to change this to the same token as on the website

    USE_PROXY
        **Default value** ``False``

    PROXY_AUTH
        **Default value** ``""``
        If you're using a proxy this needs to be set to user:passwd@proxy.bla:port

Cotiz
^^^^^

..glossary:
    :sorted:

    NONCOTIZ_CATEGORY
        **Default value** ``Non Cotiz``
        Do not change unless you know what you're doing.

    COTIZ_PRICE
        **Default value** ``1.0``
        The price of a cotiz.



Other
^^^^^

.. glossary::
    :sorted:

    DEBUG
            **Default value** ``False``

            If True, the password will never be asked

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

import json
import sys

try:
    import local_settings
except ModuleNotFoundError:
    import rapi
    if rapi.utils.check_x11():
        import gui.utils
        from PyQt5 import QtWidgets
        tmp = QtWidgets.QApplication(sys.argv)
        gui.utils.error("Error", "Can't find local_settngs.py\nRun ./bin/setup.py")
        sys.exit(5)

CACHED_SETTINGS = {}

SYNCED_SETTINGS_DEFAULT = {
    'ALCOHOL_MAJORATION': 0.0,
    'AUTH_SDE_TOKEN': 'changeme',

    'DB_HOST': "127.0.0.1",
    'USERNAME': "root",
    'PASSWORD': "",
    'DBNAME': "enibar",

    'AGIO_THRESHOLD': 14,
    'AGIO_EVERY': 7,
    'AGIO_PERCENT': 5.0,

    'NONCOTIZ_CATEGORY': "Non Cotiz",
    'COTIZ_PRICE': 1.0,

    'ECOCUP_PRICE': 1.0,
    'ECOCUP_CATEGORY': "Bar",
    'ECOCUP_PRICE_TYPES': {'take': "Achat", 'repay': "Remboursement"},
    # Note that changing the following settings will break ecocup count.
    # Do not change it unless you know what you are doing.
    'ECOCUP_NAME': "Ecocup",

    'SMTP_SERVER_ADDR': 'smtp.enib.fr',
    'SMTP_SERVER_PORT': 25,

    'WEB_URL': 'http://127.0.0.1:8000/enibar/',
    'AUTH_SDE_TOKEN': 'changeme',
    'USE_PROXY': 0,
    'PROXY_AUTH': "",
}

DEFAULT_LOCAL_SETTINGS = {
    'DEBUG': False,
    'IMG_BASE_DIR': "img/",
    'MAX_HISTORY': 5,
    'REDIS_HOST': "127.0.0.1",
    'REDIS_PASSWORD': None,
    # If this is empty, show all panels
    'SHOWN_PANELS': [],
}


class SyncedSettings:
    def __getattr__(self, name):
        if name not in SYNCED_SETTINGS_DEFAULT:
            try:
                return getattr(local_settings, name)
            except AttributeError:
                return DEFAULT_LOCAL_SETTINGS[name]

        default = SYNCED_SETTINGS_DEFAULT[name]
        if name not in CACHED_SETTINGS:
            if type(default) == dict:

                return json.loads(api.redis.get_key_blocking(name, json.dumps(default)))
            value = type(default)(api.redis.get_key_blocking(name, default).decode())
            CACHED_SETTINGS[name] = value
        return CACHED_SETTINGS[name]

    def __setattr__(self, name, value):
        if name not in SYNCED_SETTINGS_DEFAULT:
            return setattr(local_settings, name, value)

        api.redis.set_key_blocking(name, value)
        self.refresh_cache()

    def refresh_cache(self):
        global CACHED_SETTINGS
        CACHED_SETTINGS = {}


sys.modules[__name__] = SyncedSettings()

import api.redis  # nopep8
