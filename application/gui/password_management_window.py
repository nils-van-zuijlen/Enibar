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
Password Managment Window
=========================


"""

from PyQt5 import QtWidgets, uic
import api.validator
import gui.utils


class PasswordManagementWindow(QtWidgets.QDialog):
    """ Password Managment main class
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/password_management_window.ui', self)
        self.on_change = api.validator.on_change(self, self.accept_button)
        self.pseudo_input.set_validator(api.validator.NAME)
        self.old_password_input.set_validator(api.validator.NAME)
        self.new_password_input.set_validator(api.validator.NAME)
        self.show()

    def accept(self):
        """ Called when "changer" is clicked
        """
        if api.users.is_authorized(self.pseudo_input.text(),
                                   self.old_password_input.text()):
            api.users.change_password(self.pseudo_input.text(),
                                      self.new_password_input.text())
        else:
            gui.utils.error("Erreur", "L'authentification a échouée.")
        super().accept()

