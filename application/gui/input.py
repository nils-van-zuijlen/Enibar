""" Provide a fancy input.
    It needs a validator to work.
"""

from PyQt5 import QtWidgets
from PyQt5 import QtGui


class Input(QtWidgets.QLineEdit):
    """ Fancy input that takes a validator, and has a green border when ok, a
        red one when not.
    """
    def __init__(self, parent, validator):
        """
        :param QtWidget parent: The parent of the input
        :param QtValidator validator: The validator the input will use to \
        change his border.
        """
        super().__init__(parent)
        # Red by default
        self.setStyleSheet("QLineEdit{border: 1px solid red;}")
        self.textChanged.connect(self.on_change)
        self.setValidator(validator)
        self.shadow = None

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
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(0, 0)
        if self.hasAcceptableInput():
            self.set_ok()
        else:
            self.set_non_ok()

    def set_ok(self):
        """ The input content is ok, color it in green
        """
        self.setStyleSheet("QLineEdit{border: 1px solid green;}")
        self.shadow.setColor(QtGui.QColor(0, 255, 0))
        self.setGraphicsEffect(self.shadow)

    def set_non_ok(self):
        """ The input content is not ok, color it in red
        """
        self.setStyleSheet("QLineEdit{border: 1px solid red;}")
        self.shadow.setColor(QtGui.QColor(255, 0, 0))
        self.setGraphicsEffect(self.shadow)

