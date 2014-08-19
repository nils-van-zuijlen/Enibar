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
AddNote Window
====================


"""


from PyQt5 import QtWidgets, QtCore, QtGui, uic

import api.notes
import api.validator


class AddNote(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes
    """ AddNote window class """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/addnote.ui', self)

        # Add validators on inputs.
        self.nickname_input.set_validator(api.validator.NAME)
        self.name_input.set_validator(api.validator.NAME)
        self.first_name_input.set_validator(api.validator.NAME)
        self.mail_input.set_validator(api.validator.MAIL)
        self.phone_input.set_validator(api.validator.PHONE_NUMBER)
        self.birthdate_input.set_validator(api.validator.BIRTHDATE)

        self.photo_selected = None
        self.on_change = api.validator.on_change(self)
        self.show()

    def add_photo(self):
        """ Function called to add a photo. Open a QFileDialog and fill
            self.photo with the selected image
        """
        self.photo_selected = QtWidgets.QFileDialog(self).getOpenFileUrl(
            self, "Selectionnez une image", "img/",
            "Image Files (*.png *.jpg *.bmp)")[0].path()

        if self.photo_selected:
            image = QtGui.QPixmap(self.photo_selected)

            if not image.isNull():
                self.photo.setPixmap(image.scaled(QtCore.QSize(140, 120)))
                self.on_change()

    def accept(self):
        """ Called when "Ajouter" is clicked """
        super().accept()
        api.notes.add(self.nickname_input.text(),
                      self.first_name_input.text(),
                      self.name_input.text(),
                      self.mail_input.text(),
                      self.phone_input.text(),
                      self.birthdate_input.text(),
                      self.promo_input.currentText(),
                      self.photo_selected)

