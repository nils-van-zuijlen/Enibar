"""
User managment window
"""

from PyQt5 import QtWidgets
from api import users
import gui.utils


class UserManagmentWindow(QtWidgets.QDialog):
    """
    User managment window
    """
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout(self)

        self.save_button = QtWidgets.QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save)
        self.add_button = QtWidgets.QPushButton("Ajouter un utilisateur")
        self.add_button.clicked.connect(self.add)
        self.delete_button = QtWidgets.QPushButton("Supprimer l'utilisateur")
        self.delete_button.clicked.connect(self.delete)

        self.rights = {
            'manage_users': QtWidgets.QCheckBox("Gérer les utilisateurs"),
            'manage_products': QtWidgets.QCheckBox("Gérer les consomations"),
            'manage_notes': QtWidgets.QCheckBox("Gérer les notes"),
        }

        self.user_list = UserList()
        try:
            self.selected = self.user_list.widgets[0]
            self.update_form()
        except IndexError:
            self.selected = None
            for right in self.rights:
                self.rights[right].setCheckable(False)
        self.user_list.itemSelectionChanged.connect(self.select_user)

        self.layout.addWidget(self.user_list, 0, 0, len(self.rights) + 1, 3)
        for index, key in enumerate(self.rights):
            self.layout.addWidget(self.rights[key], index, 3)
        self.layout.addWidget(self.save_button, len(self.rights) + 1, 3)
        self.layout.addWidget(self.add_button, len(self.rights) + 1, 0, 1, 2)
        self.layout.addWidget(self.delete_button, len(self.rights) + 1, 2)

        self.setLayout(self.layout)
        self.show()

    def update_form(self):
        """ Fetch user rights of newly selected user
        """
        # May break if you touch it
        rights = users.get_rights(self.selected.text())
        if not rights:
            return
        for right in rights:
            self.rights[right].setChecked(rights[right])

    def select_user(self):
        """ Callback for user selection in user list
        """
        self.selected = self.user_list.currentItem()
        self.update_form()

    def delete(self):
        """ Callback to delete user when button is pushed
        """
        if users.remove(self.selected.text()):
            self.user_list.refresh()
        else:
            gui.utils.error(
                "Impossible de supprimer cet utilisateur",
                "Aucune idée du pourquoi du comment."
            )

    def add(self):
        """ Callbock to add user when button is pushed
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
        if not users.set_rights(self.selected.text(), rights):
            gui.utils.error(
                "Impossible de sauvegarder les droits",
                "erreur de communication avec la base de donnée."
            )


class UserList(QtWidgets.QListWidget):
    """ Class handling user list """
    # pylint: disable=too-many-public-methods
    def __init__(self):
        super().__init__()
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
        for user in users.get_list():
            if user not in [w.text() for w in self.widgets]:
                self.widgets.append(QtWidgets.QListWidgetItem(user, self))

        # Remove deleted users
        for widget in self.widgets:
            if widget.text() not in user_list:
                item = self.takeItem(self.row(widget))
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
            error = QtWidgets.QMessageBox()
            error.setText("Impossible d'ajouter cet utilisateur.")
            error.setInformativeText("Le nom d'utilisateur est peut "
                                     "être déja pris.")
            error.setIcon(QtWidgets.QMessageBox.Critical)
            error.exec()
