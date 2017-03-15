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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

"""
Authorization prompt
====================

Provides a decorator ask_auth.
You can use it like that:

.. code-block:: python

    @ask_auth
    def my_func():
        print("Hello world")

It will ask for a login and a password and will call your function only if it
match a combination in database.

"""


from PyQt5 import QtWidgets, uic
import api.users
import api.validator
import gui.utils
import settings
import rapi


def ask_auth(*dargs, fail_callback=None, pass_performer=False):
    """ Decorator to ask for authorization """
    def decorator(func):
        """ Decorator wrapper """
        def wrapper(*args, **kwargs):
            """ Wrapper """
            if settings.DEBUG:
                func(*args, **kwargs)
                return
            result, error = rapi.gui.check_password("manage_notes" in dargs, "manage_users" in dargs, "manage_products" in dargs)
            if result:
                if pass_performer:
                    kwargs["_performer"] = prompt.user
                func(*args, **kwargs)
            else:
                if error:
                    gui.utils.error("Error", "Erreur d'authentification")
                if fail_callback is not None:
                    fail_callback()
        return wrapper
    return decorator

