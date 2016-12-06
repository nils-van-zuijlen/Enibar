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


"""
Stats window
============

Provide neat stats
"""

from PyQt5 import QtWidgets, uic, QtCore
import api.stats


class AdminStatsWindow(QtWidgets.QDialog):
    """Admin stats window class
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/admin_stats_window.ui', self)
        nb_red, red = api.stats.get_red_sum()
        nb_green, green = api.stats.get_green_sum()
        self.red_label.setText("{:.2f} € ({})".format(red, nb_red))
        self.green_label.setText("{:.2f} € ({})".format(green, nb_green))
        self.total_label.setText("{:.2f} € ({})".format(green + red, nb_red + nb_green))
        for note, value in api.stats.get_red_notes():
            item = QtWidgets.QTreeWidgetItem(self.red_notes, [note, "{:.2f}".format(value)])
        self.show()

