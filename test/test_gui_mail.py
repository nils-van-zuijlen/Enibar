
# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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
import gui.send_mail_window
import gui.mail_selector_window
import api.notes
import api.mail


class MailTest(basetest.BaseGuiTest):

    def send_mail(self, *args):
        self.send_mail_was_called = True

    def setUp(self):
        super().setUp()
        self._reset_db()
        self.send_mail_was_called = False
        self.win = gui.send_mail_window.SendMailWindow()
        api.notes.add("Nick", "Nick", "Name", "n2name@enib.fr", "+33605040302",
            "01/02/1994", "3A", "", True, True)
        api.mail.save_model("Stock model", "Subject", "message", 0, "")
        api.mail.send_mail = self.send_mail

    def test_send_mail(self):
        """ Testing gui send mail
        """
        self.win.destinateur_input.setText("Pouette")
        self.win.subject_input.setText("Subject")
        self.win.message_input.setText("This is the message")

        def callback():
            win = self.app.activeWindow()
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.send_button.click()

        QtTest.QTest.qWait(1000)
        self.assertTrue(self.send_mail_was_called)

    def test_send_mail_reject_confirm(self):
        """ Testing send mail validation window rejection
        """
        self.win.destinateur_input.setText("Pouette")
        self.win.subject_input.setText("Subject")
        self.win.message_input.setText("This is the message")

        def callback():
            win = self.app.activeWindow()
            win.reject()
        QtCore.QTimer.singleShot(200, callback)
        self.win.send_button.click()

        QtTest.QTest.qWait(1000)
        self.assertFalse(self.send_mail_was_called)

    def test_send_mail_hidden_note(self):
        """ Testing send mail on hidden notes
        """
        self.win.destinateur_input.setText("Pouette")
        self.win.subject_input.setText("Subject")
        self.win.message_input.setText("This is the message")
        api.notes.hide(["Nick"])

        def callback():
            win = self.app.activeWindow()
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.send_button.click()

        QtTest.QTest.qWait(1000)
        self.assertFalse(self.send_mail_was_called)

    def test_new_model(self):
        """ Testing gui new model
        """
        self.win.subject_input.setText("a")
        self.win.message_input.setText("b")
        self.win.filter_selector.setCurrentIndex(1)
        self.win.filter_input.setText("c")

        def callback():
            win = self.app.activeWindow()
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.new_model_btn.trigger()
        self.assertEqual(self.win.subject_input.text(), "")
        self.assertEqual(self.win.message_input.toPlainText(), "")
        self.assertEqual(self.win.filter_selector.currentIndex(), 0)
        self.assertEqual(self.win.filter_input.text(), "")

        self.win.subject_input.setText("a")
        self.win.message_input.setText("b")
        self.win.filter_selector.setCurrentIndex(1)
        self.win.filter_input.setText("c")

        def callback():
            win = self.app.activeWindow()
            win.reject()
        QtCore.QTimer.singleShot(200, callback)
        self.win.new_model_btn.trigger()
        self.assertEqual(self.win.subject_input.text(), "a")
        self.assertEqual(self.win.message_input.toPlainText(), "b")
        self.assertEqual(self.win.filter_selector.currentIndex(), 1)
        self.assertEqual(self.win.filter_input.text(), "c")

    def test_save_model(self):
        """ Testing gui save model
        """
        def callback():
            win = self.app.activeWindow()
            win.input.setText("Model")
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.save_model_btn.trigger()
        self.assertTrue(api.mail.get_models(name="Model"))

    def test_load_model(self):
        """ Testing gui load model
        """
        def callback():
            win = self.app.activeWindow()
            models = self.get_items(win.model_list)
            index = models.index("Stock model")
            win.model_list.setCurrentRow(index)
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.open_model_btn.trigger()
        self.assertEqual(self.win.subject_input.text(), "Subject")
        self.assertEqual(self.win.filter_selector.currentIndex(), 0)
        self.assertEqual(self.win.filter_input.text(), "")
        self.assertEqual(self.win.message_input.toPlainText(), "message")

        def callfail():
            win = self.app.activeWindow()
            win.model_list.setCurrentRow(152134)
            win.accept()
        QtCore.QTimer.singleShot(200, callfail)
        self.win.open_model_btn.trigger()

    def test_model_deletion(self):
        """ Testing gui model deletion
        """
        def callback():
            win = self.app.activeWindow()
            before_list = self.get_items(win.model_list)
            win.model_list.setCurrentRow(0)
            QtTest.QTest.keyPress(win, QtCore.Qt.Key_Delete)
            after_list = self.get_items(win.model_list)
            self.assertNotEqual(before_list, after_list)
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.open_model_btn.trigger()
        self.assertEqual([], list(api.mail.get_models()))

        def callback():
            win = self.app.activeWindow()
            before_list = self.get_items(win.model_list)
            win.model_list.setCurrentRow(150)
            QtTest.QTest.keyPress(win, QtCore.Qt.Key_Delete)
            after_list = self.get_items(win.model_list)
            self.assertEqual(before_list, after_list)
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.win.open_model_btn.trigger()

    def test_filter_selector(self):
        """ Testing filter selector
        """
        self.win.filter_selector.setCurrentIndex(0)
        self.assertFalse(self.win.filter_input.isEnabled())
        for i in [1, 2, 3]:
            self.win.filter_selector.setCurrentIndex(i)
            self.assertTrue(self.win.filter_input.isEnabled())

    def test_filter_input_click(self):
        """ Testing filter input click
        """
        def callback():
            win = self.app.activeWindow()
            instance = isinstance(win, gui.mail_selector_window.MailSelectorWindow)
            self.assertFalse(instance)
            if instance:
                win.accept()

        self.win.filter_selector.setCurrentIndex(0)
        QtCore.QTimer.singleShot(200, callback)
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)

        QtTest.QTest.qWait(300)
        self.win.filter_selector.setCurrentIndex(2)
        QtCore.QTimer.singleShot(200, callback)
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)

        QtTest.QTest.qWait(300)
        self.win.filter_selector.setCurrentIndex(3)
        QtCore.QTimer.singleShot(200, callback)
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)

        # test Standaloe MailFilterSelector
        mfs = gui.mail_widget.MailFilterSelector(self.win)
        self.assertRaises(ValueError, mfs.update_filter, 0)
        mfi = gui.mail_widget.MailFilterInput(self.win)
        mfs.set_filter_input(mfi)
        mfs.update_filter(0)
        self.assertFalse(mfs.filter_input.isEnabled())

        def callback():
            win = self.app.activeWindow()
            instance = isinstance(win, gui.mail_selector_window.MailSelectorWindow)
            self.assertTrue(instance)
            item = win.mail_list.topLevelItem(0)
            win.mail_list.setCurrentItem(item)
            win.accept()

        QtTest.QTest.qWait(300)
        self.win.filter_selector.setCurrentIndex(1)
        QtCore.QTimer.singleShot(200, callback)
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)
        self.assertEqual(self.win.filter_input.text(), "n2name@enib.fr")

        def callback():
            win = self.app.activeWindow()
            instance = isinstance(win, gui.mail_selector_window.MailSelectorWindow)
            self.assertTrue(instance)
            items = win.mail_list.selectedItems()
            self.assertEqual(len(items), 1)
            win.accept()

        QtTest.QTest.qWait(300)
        QtCore.QTimer.singleShot(200, callback)
        self.win.filter_input.setText("n2name@enib.fr")
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)

        def callback():
            win = self.app.activeWindow()
            instance = isinstance(win, gui.mail_selector_window.MailSelectorWindow)
            self.assertTrue(instance)
            items = win.mail_list.selectedItems()
            self.assertEqual(len(items), 0)
            win.accept()

        QtTest.QTest.qWait(300)
        QtCore.QTimer.singleShot(200, callback)
        self.win.filter_input.setText("")
        QtTest.QTest.mouseClick(self.win.filter_input, QtCore.Qt.LeftButton)

    def test_completion(self):
        """ Testing message completion
        """
        QtTest.QTest.mousePress(self.win.message_input, QtCore.Qt.LeftButton)
        self.win.message_input.setText("sur")
        QtTest.QTest.qWait(300)
        QtTest.QTest.keyPress(self.win.message_input, QtCore.Qt.Key_Right)
        QtTest.QTest.keyPress(self.win.message_input, QtCore.Qt.Key_Right)
        QtTest.QTest.keyPress(self.win.message_input, QtCore.Qt.Key_Right)
        QtTest.QTest.keyPress(self.win.message_input, QtCore.Qt.Key_Tab)
        QtTest.QTest.keyPress(self.win.message_input, QtCore.Qt.Key_Enter)
        self.assertTrue(self.win.message_input.toPlainText(), "{surnom}")

