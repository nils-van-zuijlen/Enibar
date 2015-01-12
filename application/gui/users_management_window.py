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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

"""
User managment window
"""

from PyQt5 import QtWidgets
from PyQt5 import uic
from api import users
import gui.utils


class UsersManagementWindow(QtWidgets.QDialog):
    """
    User managment window
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/users_management_window.ui', self)

        self.save_button.clicked.connect(self.save)
        self.add_button.clicked.connect(self.add)
        self.delete_button.clicked.connect(self.delete)
        self.rights = {
            'manage_users': self.manage_users,
            'manage_products': self.manage_products,
            'manage_notes': self.manage_notes,
        }
        try:
            self.selected = self.user_list.widgets[0]
            self.update_form()
        except IndexError:
            self.selected = None
            self.set_form_checkable(False)

        self.show()

    def set_form_checkable(self, checkable):
        """ Set form state

        :param bool checkable: Futur checkbox state
        """
        for right in self.rights:
            self.rights[right].setCheckable(checkable)
            if not checkable:
                self.rights[right].setCheckState(0)

    def update_form(self):
        """ Fetch user rights of newly selected user
        """
        rights = users.get_rights(self.selected.text())
        for right in rights:
            self.rights[right].setChecked(rights[right])
        self.set_form_checkable(True)

    def select_user(self, item):
        """ Callback for user selection in user list
        """
        self.selected = item
        self.update_form()

    def delete(self):
        """ Callback to delete user when button is pushed
        """
        if not self.selected:
            gui.utils.error("Impossible de supprimer l'utilisateur",
                            "Aucun utilisateur selectionné")
            return
        users.remove(self.selected.text())
        self.user_list.refresh()

    def add(self):
        """ Callback to add user when button is pushed
        """
        prompt = AddUserPrompt()
        if prompt.exec():
            self.user_list.refresh()

    def save(self):
        """ Callback to save user when button is pushed
        """
        if not self.selected:
            gui.utils.error(
                "Impossible de sauvegarder les droits",
                "Aucun utilisateur n'est selectionné"
            )
            return
        rights = {key: value.isChecked() for key, value in self.rights.items()}
        users.set_rights(self.selected.text(), rights)
        self.user_list.refresh()


class UserList(QtWidgets.QListWidget):
    """ Class handling user list """
    def __init__(self, parent):
        super().__init__(parent)
        super().setSortingEnabled(True)
        self.widgets = []
        for user in users.get_list():
            widget = QtWidgets.QListWidgetItem(user, self)
            self.widgets.append(widget)
        if len(self.widgets):
            self.widgets[0].setSelected(True)

    def refresh(self):
        """ Refesh list and add user which are not present
        """
        user_list = list(users.get_list())
        # Add added users
        for user in user_list:
            if user not in [w.text() for w in self.widgets]:
                self.widgets.append(QtWidgets.QListWidgetItem(user, self))

        # Remove deleted users
        for widget in self.widgets:
            if widget.text() not in user_list:
                item = self.takeItem(self.row(widget))
                self.widgets.pop(self.widgets.index(widget))
                del item


class AddUserPrompt(QtWidgets.QDialog):
    """ Class handling user creation prompt
    """
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout()
        self.setStyleSheet("QPushButton{margin:0.5em 0 0 0;padding:0.25em 1em}")

        self.username_label = QtWidgets.QLabel("Nom d'utilisateur:", self)
        self.password_label = QtWidgets.QLabel("Mot de passe:", self)
        self.username_input = QtWidgets.QLineEdit(self)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.cancel_button = QtWidgets.QPushButton("Annuler", self)
        self.validation_button = QtWidgets.QPushButton("Ajouter", self)

        self.layout.addWidget(self.username_label, 0, 0)
        self.layout.addWidget(self.username_input, 1, 0, 1, 0)
        self.layout.addWidget(self.password_label, 2, 0)
        self.layout.addWidget(self.password_input, 3, 0, 1, 0)
        self.layout.addWidget(self.validation_button, 4, 0)
        self.layout.addWidget(self.cancel_button, 4, 1)

        self.cancel_button.setAutoDefault(False)
        self.setLayout(self.layout)

        self.cancel_button.clicked.connect(self.reject)
        self.validation_button.clicked.connect(self.accept)

    def accept(self):
        """ Callback to create user when validation button is pressed
        """
        if users.add(self.username_input.text(), self.password_input.text()):
            super().accept()
        else:
            gui.utils.error("Impossible d'ajouter cet utilisateur.",
                            "Le nom d'utilisateur est peut être déjà pris.")

