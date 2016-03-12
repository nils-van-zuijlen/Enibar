# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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

from PyQt5 import QtCore
import basetest
import settings
import gui.settings_window


class SettingsGuiTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        settings.synced.ALCOHOL_MAJORATION = 0
        settings.synced.refresh_cache()
        self.win = gui.settings_window.SettingsWindow()

    def test_changing_setting(self):
        """ Testing changing a setting. """
        def callback():
            settings.synced.refresh_cache()
            self.assertEqual(settings.synced.ALCOHOL_MAJORATION, 4.0)
            self.app.exit()
        self.win.majoration_input.setText("4")
        QtCore.QTimer.singleShot(200, callback)
        self.win.accept()
        self.app.exec_()

