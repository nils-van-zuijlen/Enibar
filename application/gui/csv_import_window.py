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
CsvImportWindow
===============

A window that show a recap of a csv import
"""

from PyQt5 import QtWidgets, uic, QtCore
import api.notes
import api.validator
import csv
import gui.utils


class CsvImportWindow(QtWidgets.QDialog):
    """ CsvImportWindow class
    """
    def __init__(self, path):
        super().__init__()
        uic.loadUi('ui/csv_import_window.ui', self)
        self.file_path = path
        self.notes = []
        self.on_change = lambda: False
        self.amount.setValidator(api.validator.NUMBER)
        self.reason.setValidator(api.validator.NAME)
        self.recap.header().setStretchLastSection(False)
        self.recap.header().setSectionResizeMode(1,
            QtWidgets.QHeaderView.Stretch)
        self._build_recap()
        self.show()

    def _build_recap(self):
        """ Parse a CSV file and try to build lines from it.
        """
        with open(self.file_path, 'r', encoding="ISO8859") as fd:
            reader = csv.DictReader(fd)
            for line in reader:
                try:
                    mail = line['Email']
                    note = api.notes.get(lambda x: x['mail'] == mail)
                    if note:
                        note = note[0]['nickname']
                        self.notes.append(note)
                except ValueError:
                    continue
                if note:
                    QtWidgets.QTreeWidgetItem(
                        self.recap,
                        (note,
                         mail
                        )
                    )
                else:
                    w = QtWidgets.QTreeWidgetItem(
                        self.recap,
                        ("[{} {}]".format(line["Nom"], line["Prenom"]),
                         mail
                        )
                    )
                    for i in range(2):
                        w.setBackground(i, QtCore.Qt.red)

    def on_validation(self):
        """ Called when "Valider" is clicked
        """
        if float(self.amount.text()) > 0.01:
            api.notes.import_csv(
                self.notes,
                self.reason.text(),
                -float(self.amount.text()),
                do_not=True
            )
            api.notes.rebuild_cache()
            self.close()
        else:
            gui.utilse.error("Erreur", "Verifiez le montant")

