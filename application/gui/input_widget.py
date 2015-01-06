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


""" Provide a fancy input.
    It needs a validator to work.
"""

from PyQt5 import QtWidgets, QtGui


class Input(QtWidgets.QLineEdit):
    """ Fancy input that takes a validator, and has a green border when ok, a
        red one when not.
    """
    def __init__(self, parent):
        """
        :param QtWidget parent: The parent of the input
        """
        super().__init__(parent)
        # Red by default
        self.setStyleSheet("QLineEdit:enabled{border: 1px solid red;\
                            padding:2px}")
        self.textChanged.connect(self.on_change)
        self.shadow = None
        self.valid = False

    def set_validator(self, validator):
        """ Set a validator to the input

        :param QtValidator validator: The validator the input will use to \
        change his border.
        """
        self.setValidator(validator)
        self.on_change()

    def event(self, event):
        """ Overwrite event management from qt to catch the focus of the input
            :param QEvent event: An event
        """
        if isinstance(event, QtGui.QFocusEvent):
            if event.gotFocus():
                self.on_change()
            else:
                self.setGraphicsEffect(None)
        return super().event(event)

    def on_change(self):
        """ Called when the input changes or on focus
        """
        # We need to reconstruct the shadow each time, Qt destroy it when we
        # call self.setGraphicsEffect(None)
        if not self.isEnabled():
            self.setGraphicsEffect(None)
            return
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(0, 0)
        if self.hasAcceptableInput():
            self.set_ok()
            try:
                self.parent().on_change()
            except AttributeError:
                pass
        else:
            self.set_non_ok()
            self.parent().on_change()

    def set_ok(self):
        """ The input content is ok, color it in green
        """
        self.valid = True
        self.setStyleSheet("QLineEdit:enabled{border: 1px solid green;\
                            padding:2px;}")
        self.shadow.setColor(QtGui.QColor(0, 255, 0))
        self.setGraphicsEffect(self.shadow)

    def set_non_ok(self):
        """ The input content is not ok, color it in red
        """
        self.valid = False
        self.setStyleSheet("QLineEdit:enabled{border: 1px solid red;\
                            padding:2px;}")
        self.shadow.setColor(QtGui.QColor(255, 0, 0))
        self.setGraphicsEffect(self.shadow)

