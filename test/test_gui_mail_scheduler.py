

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

from PyQt5 import QtCore, QtWidgets, QtTest, QtGui
import time
import basetest
import gui.mail_scheduler_window
import api.notes
import api.mail


class MailTest(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        api.notes.add("Nick", "Nick", "Name", "n2name@enib.fr", "+33605040302",
            "01/02/1994", "3A", "", True, True)
        api.mail.save_model("Stock model", "Subject", "message", 0, "")
        api.mail.save_scheduled_mails("Scheduled Mail 1", False, 1, "day", 0,
            0, "", "Scheduled mail test 1", "test@test.com",
            "This is a massage", None
        )
        self.win = gui.mail_scheduler_window.MailSchedulerWindow(None)

    def test_startup_state(self):
        """ Testing mail scheduler startup state
        """
        self.assertTrue(self.win.description_groupbox.isEnabled())
        self.assertTrue(self.win.status_groupbox.isEnabled())
        self.assertTrue(self.win.schedule_groupbox.isEnabled())
        self.assertTrue(self.win.filter_groupbox.isEnabled())
        self.assertTrue(self.win.message_groupbox.isEnabled())

    def test_mail_list(self):
        """ Testing mail scheduler list
        """
        self.assertEqual(self.win.scheduled_mails_list.count(), 1)
        self.assertEqual(self.win.name_input.text(), "Scheduled Mail 1")
        self.win.build_mail_list()
        self.assertEqual(self.win.scheduled_mails_list.count(), 1)

        # test empty list
        api.mail.delete_scheduled_mail("Scheduled Mail 1")
        self.win.build_mail_list()
        self.assertEqual(self.win.scheduled_mails_list.count(), 0)

    def test_rename_current_mail(self):
        """ Testing rename current mail
        """
        QtTest.QTest.mouseClick(self.win.name_input, QtCore.Qt.LeftButton)
        self.win.name_input.setText("New name")
        QtTest.QTest.keyPress(self.win.name_input, QtCore.Qt.Key_Enter)
        self.assertEqual(len(list(api.mail.get_scheduled_mails(name="New name"))), 1)
        self.assertEqual(len(list(api.mail.get_scheduled_mails(name="Scheduled Mail 1"))), 0)
        self.assertEqual(self.win.scheduled_mails_list.count(), 1)

        QtTest.QTest.mouseClick(self.win.name_input, QtCore.Qt.LeftButton)
        self.win.name_input.setText("New name")
        QtTest.QTest.keyPress(self.win.name_input, QtCore.Qt.Key_Enter)
        self.assertEqual(len(list(api.mail.get_scheduled_mails(name="New name"))), 1)
        self.assertEqual(self.win.scheduled_mails_list.count(), 1)

    def test_delete_mail(self):
        """ Testing mail deletion
        """

        QtTest.QTest.keyPress(self.win.scheduled_mails_list, QtCore.Qt.Key_Delete)
        self.win.build_mail_list()
        self.assertEqual(self.win.scheduled_mails_list.count(), 0)

        # Also test for correct editor state as we remove last mail
        self.assertFalse(self.win.description_groupbox.isEnabled())
        self.assertFalse(self.win.status_groupbox.isEnabled())
        self.assertFalse(self.win.schedule_groupbox.isEnabled())
        self.assertFalse(self.win.filter_groupbox.isEnabled())
        self.assertFalse(self.win.message_groupbox.isEnabled())

        # test delete when not selected
        self.win.scheduled_mails_list.setCurrentRow(42)
        QtTest.QTest.keyPress(self.win.scheduled_mails_list, QtCore.Qt.Key_Delete)
        self.win.build_mail_list()
        self.assertEqual(self.win.scheduled_mails_list.count(), 0)

        # Check that another key don't delete mail
        # stupid but coverage
        api.mail.save_scheduled_mails("Scheduled Mail 2", False, 1, "day", 0,
            0, "", "Scheduled mail test 2", "test@test.com",
            "This is a massage", None
        )
        self.win.build_mail_list()
        QtTest.QTest.keyPress(self.win.scheduled_mails_list, QtCore.Qt.Key_Enter)
        self.assertEqual(self.win.scheduled_mails_list.count(), 1)

    def test_save_model(self):
        """ Testing gui save model from mail scheduler
        """
        def callback():
            win = self.app.activeWindow()
            win.input.setText("Model")
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.save_model.trigger()
        self.assertTrue(api.mail.get_models(name="Model"))

    def test_load_model(self):
        """ Testing gui load model from mail scheduled
        """
        def callback():
            win = self.app.activeWindow()
            models = self.get_items(win.model_list)
            index = models.index("Stock model")
            win.model_list.setCurrentRow(index)
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.load_model.trigger()
        self.assertEqual(self.win.subject_input.text(), "Subject")
        self.assertEqual(self.win.filter_selector.currentIndex(), 0)
        self.assertEqual(self.win.filter_input.text(), "")
        self.assertEqual(self.win.message_input.toPlainText(), "message")

    def test_new_mail(self):
        """ Testing new scheduled mail
        """
        self.win.new_mail.trigger()
        self.assertEqual(self.win.scheduled_mails_list.count(), 2)
        self.assertEqual(self.win.name_input.text(), "Brouillon")
        self.assertFalse(self.win.active_checkbox.isChecked())
        self.assertEqual(self.win.schedule_interval.value(), 1)
        self.assertEqual(self.win.schedule_interval_unit.currentIndex(), 0)
        self.assertEqual(self.win.schedule_day.currentIndex(), 0)
        self.assertEqual(self.win.filter_selector.currentIndex(), 0)
        self.assertFalse(self.win.filter_input.isEnabled())
        self.assertEqual(self.win.subject_input.text(), "")
        self.assertEqual(self.win.message_input.toPlainText(), "")

    def test_save_scheduled_mail(self):
        """ Testing save scheduled mail
        """
        self.win.message_input.setText("This is a new text.")
        self.win.save_scheduled_mail.trigger()
        mail = list(api.mail.get_scheduled_mails(name="Scheduled Mail 1"))[0]
        self.assertEqual(mail['message'], "This is a new text.")
