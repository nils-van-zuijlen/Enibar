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


from PyQt5 import QtWidgets


def ask_auth(func):
    """ Decorator to ask for authorization """
    def wrapper(*args, **kwargs):
        """ Wrapper """
        prompt = AuthPrompt()
        if prompt.is_authorized:
            func(*args, **kwargs)
        else:
            print("Nope")
    return wrapper


class AuthPrompt(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes
    """ Authorization prompt class """
    def __init__(self):
        super().__init__()
        self.is_authorized = False

        self.layout = QtWidgets.QGridLayout()
        self.setStyleSheet("QPushButton{margin:0.5em 0 0 0;padding:0.25em 1em}")

        self.login_label = QtWidgets.QLabel("Login:", self)
        self.pass_label = QtWidgets.QLabel("Password:", self)
        self.login_input = QtWidgets.QLineEdit(self)
        self.pass_input = QtWidgets.QLineEdit(self)

        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.reject_button = QtWidgets.QPushButton("Cancel", self)
        self.accept_button = QtWidgets.QPushButton("Login", self)

        self.layout.addWidget(self.login_label, 0, 0)
        self.layout.addWidget(self.login_input, 1, 0, 1, 0)
        self.layout.addWidget(self.pass_label, 2, 0)
        self.layout.addWidget(self.pass_input, 3, 0, 1, 0)
        self.layout.addWidget(self.accept_button, 4, 0)
        self.layout.addWidget(self.reject_button, 4, 1)

        self.reject_button.setAutoDefault(False)
        self.setLayout(self.layout)

        self.reject_button.clicked.connect(self.reject)
        self.accept_button.clicked.connect(self.accept)

        self.exec()

    def accept(self):
        """ Called when "Login" is clicked """
        if self.login_input.text() == "test":
            self.is_authorized = True
        else:
            self.is_authorized = False
        super().accept()

