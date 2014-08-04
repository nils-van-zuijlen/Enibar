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


from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import api.notes
import api.validator
from .input import Input


class AddNote(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes
    """ Authorization prompt class """
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout()

        self.pseudo_label = QtWidgets.QLabel("Surnom:", self)
        self.name_label = QtWidgets.QLabel("Nom:", self)
        self.surname_label = QtWidgets.QLabel("Prénom:", self)
        self.birthdate_label = QtWidgets.QLabel("Date de naissance:", self)
        self.promo_label = QtWidgets.QLabel("Promo:", self)
        self.mail_label = QtWidgets.QLabel("Mail:", self)
        self.phone_label = QtWidgets.QLabel("Téléphone:", self)
        self.photo_label = QtWidgets.QLabel("Photo: ", self)
        self.image = QtWidgets.QLabel(self)
        self.image.setAlignment(QtCore.Qt.AlignCenter)

        self.pseudo_input = Input(self, api.validator.NAME)
        self.name_input = Input(self, api.validator.NAME)
        self.surname_input = Input(self, api.validator.NAME)
        self.birthdate_input = Input(self, api.validator.BIRTHDATE)
        self.promo_input = QtWidgets.QComboBox(self)
        self.promo_input.insertItems(0, ["1A", "2A", "3A", "3S", "4A", "5A",
                                         "Esiab", "Externe", "Ancien", "Prof"])
        self.mail_input = Input(self, api.validator.MAIL)
        self.phone_input = Input(self, api.validator.PHONE_NUMBER)
        self.photo_input_button = QtWidgets.QPushButton("Ajouter une photo")
        self.photo_input_button.clicked.connect(self.add_photo)

        self.reject_button = QtWidgets.QPushButton("Cancel", self)
        self.accept_button = QtWidgets.QPushButton("Ajouter", self)
        self.accept_button.setEnabled(False)

        self.layout.addWidget(self.pseudo_label, 1, 0)
        self.layout.addWidget(self.pseudo_input, 2, 0, 1, 0)
        self.layout.addWidget(self.name_label, 3, 0)
        self.layout.addWidget(self.name_input, 4, 0, 1, 0)
        self.layout.addWidget(self.surname_label, 5, 0)
        self.layout.addWidget(self.surname_input, 6, 0, 1, 0)
        self.layout.addWidget(self.birthdate_label, 7, 0)
        self.layout.addWidget(self.birthdate_input, 8, 0, 1, 0)
        self.layout.addWidget(self.promo_label, 9, 0)
        self.layout.addWidget(self.promo_input, 10, 0, 1, 0)
        self.layout.addWidget(self.mail_label, 11, 0)
        self.layout.addWidget(self.mail_input, 12, 0, 1, 0)
        self.layout.addWidget(self.phone_label, 13, 0)
        self.layout.addWidget(self.phone_input, 14, 0, 1, 0)
        self.layout.addWidget(self.photo_label, 15, 0)
        self.layout.addWidget(self.photo_input_button, 16, 0, 1, 0)
        self.layout.addWidget(self.accept_button, 18, 0)
        self.layout.addWidget(self.reject_button, 18, 1)

        self.reject_button.setAutoDefault(False)
        self.setLayout(self.layout)

        self.accept_button.clicked.connect(self.accept)
        self.reject_button.clicked.connect(self.reject)

        self.photo_selected = None
        self.show()

    def add_photo(self):
        """ Function called to add a photo. Open a QFileDialog and fill
            self.image with the selected image
        """
        self.photo_selected = QtWidgets.QFileDialog(self).getOpenFileUrl(
            self, "Selectionnez une image", "img/",
            "Image Files (*.png *.jpg *.bmp)")[0].path()

        if self.photo_selected:
            image = QtGui.QPixmap(self.photo_selected)

            if not image.isNull():
                self.image.setPixmap(image.scaled(QtCore.QSize(140, 120)))
                self.layout.addWidget(self.image, 17, 0, 1, 0)

    def accept(self):
        """ Called when "Ajouter" is clicked """
        super().accept()
        api.notes.add(self.pseudo_input.text(),
                      self.surname_input.text(),
                      self.name_input.text(),
                      self.mail_input.text(),
                      self.phone_input.text(),
                      self.birthdate_input.text(),
                      self.promo_input.currentText(),
                      self.photo_selected)

    def on_change(self):
        """ Called when an Input goes from red to green
        """
        for _, obj in self.__dict__.items():
            if isinstance(obj, Input):
                if not obj.valid:
                    self.accept_button.setEnabled(False)
                    return
        self.accept_button.setEnabled(True)

