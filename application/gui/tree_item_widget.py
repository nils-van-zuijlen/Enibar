# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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

TreeWidget
==========

This is a custom implementation of a QTreeWidgetItem.
It changes the function to sort the Widgets between them
to allow a sort by numbers.
"""

from PyQt5 import QtWidgets


class TreeWidget(QtWidgets.QTreeWidgetItem):
    """ TreeWidget class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree_widget = self.treeWidget()

    def __lt__(self, other):
        column = self.tree_widget.sortColumn()
        try:
            return float(self.text(column)) < float(other.text(column))
        except:
            return super().__lt__(other)
