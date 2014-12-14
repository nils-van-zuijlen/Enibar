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
Stats window
============

Provide neat stats
"""

from PyQt5 import QtWidgets, QtCore, uic
import api.stats


class StatsWindow(QtWidgets.QDialog):
    """Stats window class
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/stats_window.ui', self)

        self.show()
        self.refresh_stats()

    def refresh_stats(self):
        """ Refresh the stats of the window
        """
        red = api.stats.get_red()
        green = api.stats.get_green()
        sold_items = list(api.stats.get_sold_items())
        consumers = list(api.stats.get_consumers())
        if not sold_items or not consumers:
            return
        most_sold = sorted(sold_items, key=lambda x: x['nb'])[-1]
        most_refilled = sorted(consumers, key=lambda x: x['refilled'])[-1]
        most_bought = sorted(consumers, key=lambda x: x['bought'])[-1]

        self.red_value.setText("{:.2f}€ ({} note{})".format(
            red['total_red'],
            red['nb_notes'],
            's' * (red['nb_notes'] > 1))
        )
        self.green_value.setText("{:.2f}€ ({} note{})".format(
            green['total_green'],
            green['nb_notes'],
            's' * (green['nb_notes'] > 1))
        )
        name = "{} ({}) - {}".format(most_sold['product'],
                                     most_sold['price_name'],
                                     most_sold['category'])

        self.most_sold_value.setText("{} ({} vendu{})".format(
            name, most_sold['nb'], 's' * (most_sold['nb'] > 1)))
        self.most_refilled_value.setText("{} ({:.2f}€)".format(
            most_refilled['note'],
            most_refilled['refilled'], )
        )
        self.most_bought_value.setText("{} ({:.2f}€)".format(
            most_bought['note'],
            most_bought['bought'], )
        )

