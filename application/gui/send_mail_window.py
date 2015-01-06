from PyQt5 import QtCore, QtWidgets, uic
from .mail_selector_window import MailSelectorWindow
import api.mail


class SendMailWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi('ui/send_mail_window.ui', self)

        # Default value for inputs
        self.destinateur_input.setText("cafeteria@enib.fr")

        # Bind mouse event of filter input
        self.filter_input.mousePressEvent = self.on_filter_input_click

        # Filters function used to select valid notes from selected filter
        self.filters = [
            lambda x, y: True,
            lambda x, y: x['mail'] in y.split(','),
            lambda x, y: x['note'] >= float(y),
            lambda x, y: x['note'] < float(y),
        ]

        # Show window
        self.show()

    def send(self):
        recipients = self.get_recipient_list()
        for recipient in recipients:
            api.mail.send_mail(
                recipient['mail'],
                self.subject_input.text(),
                api.mail.format_message(self.message_input.toPlainText(), recipient),
                self.destinateur_input.text(),
            )

    def on_filter_selector_change(self, selected):
        if selected == 0:
            self.filter_input.setEnabled(False)
        else:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("")

            if selected == 1:
                self.filter_input.setPlaceholderText(
                    "Cliquez pour selctionner des notes"
                )
            elif selected >= 2:
                self.filter_input.setPlaceholderText("Montant à comparer")

    def on_filter_input_click(self, event):
        if self.filter_selector.currentIndex() != 1:
            return
        popup = MailSelectorWindow(self, self.filter_input.text().split(','))
        if popup.exec():
            mails = popup.get_mail_list()
            self.filter_input.setText(','.join(mails))

    def get_recipient_list(self):
        try:
            filter_fnc = self.filters[self.filter_selector.currentIndex()]
        except KeyError:
            return

        arg = self.filter_input.text()
        return api.notes.get(lambda x: filter_fnc(x, arg))


