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

"""
SettingsWindow
====================


"""


from PyQt5 import QtWidgets, uic
import api.validator
import api.redis
import settings


class SettingsWindow(QtWidgets.QDialog):
    """ RefillNote window class """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/settings_window.ui', self)
        self.majoration_input.set_validator(api.validator.NUMBER)
        self.majoration_input.setText(str(settings.synced.ALCOHOL_MAJORATION))
        self.key_input.set_validator(api.validator.NOTHING)
        self.key_input.setText(str(settings.synced.AUTH_SDE_TOKEN))
        self.show()

    def accept(self):
        """ Called when "Sauvegarder" is clicked
        """
        settings.synced.ALCOHOL_MAJORATION = float(self.majoration_input.text())
        settings.synced.AUTH_SDE_TOKEN = self.key_input.text()
        api.redis.send_message("enibar-settings", "")
        super().accept()

    def on_change(self):
        self.save_button.setEnabled(self.key_input.valid and self.majoration_input.valid)

