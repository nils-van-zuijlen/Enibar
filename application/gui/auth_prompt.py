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
from api import users


def ask_auth(*dargs):
    """ Decorator to ask for authorization """
    def decorator(func):
        """ Decorator wrapper """
        def wrapper(*args, **kwargs):
            """ Wrapper """
            prompt = AuthPrompt(dargs)
            prompt.exec()
            if prompt.is_authorized:
                func(*args, **kwargs)
            else:
                print("Nope")
        return wrapper
    return decorator


class AuthPrompt(QtWidgets.QDialog):
    """ Authorization prompt class """
    def __init__(self, requirements):
        super().__init__()
        self.requirements = requirements
        uic.loadUi('ui/authprompt.ui', self)
        self.is_authorized = False

    def accept(self):
        """ Called when "Login" is clicked """
        if users.is_authorized(self.login_input.text(), self.pass_input.text()):
            rights = users.get_rights(self.login_input.text())
            for requirement in self.requirements:
                if not rights[requirement]:
                    return super().accept()
            self.is_authorized = True
        else:
            self.is_authorized = False
        return super().accept()

