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

from PyQt5 import QtWidgets, uic
import api.notes
import gui.utils
import re


class CsvImportWindow(QtWidgets.QDialog):
    """ CsvImportWindow class
    """
    def __init__(self, path):
        super().__init__()
        uic.loadUi('ui/csv_import_window.ui', self)
        self.file_path = path
        self.recap.header().setStretchLastSection(False)
        self.recap.header().setSectionResizeMode(1,
            QtWidgets.QHeaderView.Stretch)
        self._build_recap()
        self.show()

    def _parse_line(self, line):
        """ Parse a CSV line and returns a recap
        """
        _, _, _, note, _, _, _, amount, motive = line.split(',')
        if all([note, amount, motive]):
            if api.notes.get(lambda x: x['nickname'].lower() == note.lower()):
                return note.strip(), float(amount), motive.strip()
        raise ValueError

    def _build_recap(self):
        """ Parse a CSV file and try to build lines from it.
        """
        with open(self.file_path, 'r') as fd:
            for line in fd:
                re.sub("\"(\d+?),(\d+?)\"", "\1.\2", line)
                try:
                    note, amount, motive = self._parse_line(line)
                except ValueError:
                    continue
                amount = round(amount, 2)
                QtWidgets.QTreeWidgetItem(
                    self.recap,
                    (note,
                     motive,
                     "{} €".format(-amount) if amount < 0 else "-",
                     "{} €".format(amount) if amount > 0 else "-"
                    )
                )

    def on_validation(self):
        """ Called when "Valider" is clicked
        """
        with open(self.file_path, 'r') as fd:
            nb_op = api.notes.import_csv(fd.read(), do_not=True)
        api.notes.rebuild_cache()
        gui.utils.valid("{} opération{s} effectuée{s}".format(nb_op,
            s="s" * (nb_op > 1)))
        self.close()

