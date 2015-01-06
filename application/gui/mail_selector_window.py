from PyQt5 import QtCore, QtWidgets, uic, QtGui
import api.notes


class MailSelectorWindow(QtWidgets.QDialog):
    def __init__(self, parent, mails):
        super().__init__(parent)
        uic.loadUi("ui/mail_selector_window.ui", self)
        self.load_list(mails)

    def load_list(self, mails):
        for note in api.notes.get():
            widget = QtWidgets.QTreeWidgetItem(self.mail_list,(
                note['nickname'],
                note['mail'],
                note['firstname'],
                note['lastname']
            ))
            if note['mail'] in mails:
                widget.setSelected(True)

    def get_mail_list(self):
        mails = []
        for line in self.mail_list.selectedIndexes():
            mail = self.mail_list.topLevelItem(line.row()).text(1)
            if mail not in mails:
                mails.append(mail)
        return mails
