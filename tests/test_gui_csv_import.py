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

from PyQt5 import QtCore, QtWidgets
import api.notes
import basetest
import gui.csv_import_window


class CsvImportTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.add_note("test", mail="test@test.fr")
        self.add_note("test2", mail="test2@test.fr")
        self.win = gui.csv_import_window.CsvImportWindow("../tests/resources/test.csv")

    def test_import(self):
        """ Testing csv import """
        self.win.reason.setText("coucou")
        self.win.amount.setText("20")
        self.win.validation_button.click()
        self.assertEqual(self.get_tree(self.win.recap),
        [{('test2', 'test2@test.fr'): []}, {('test', 'test@test.fr'): []}, {('[test test]', 'test3@test.fr'): []}, {('[a b]', ''): []}])
        self.assertEqual(self.win.recap.topLevelItem(2).background(0), QtCore.Qt.red)
        self.assertEqual(self.win.recap.topLevelItem(3).background(0), QtCore.Qt.red)
        for note in api.notes.get():
            self.assertEqual(note['note'], -20)

    def test_import_fail(self):
        """ Testing csv import with bad amount
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("montant", win.informativeText())
            for note in api.notes.get():
                self.assertEqual(note['note'], 0)
            win.accept()
        self.win.reason.setText("coucou")
        self.win.amount.setText("0.0001")
        QtCore.QTimer.singleShot(200, callback)
        self.win.validation_button.click()

