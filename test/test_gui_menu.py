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

import gui.main_window
import basetest

from gui.products_management_window import ProductsManagementWindow
from gui.empty_note_window import EmptyNoteWindow
from gui.notes_management_window import NotesManagementWindow
from gui.group_actions_window import GroupActionsWindow
from gui.panels_management_window import PanelsManagementWindow
from gui.password_management_window import PasswordManagementWindow
from gui.refill_note_window import RefillNoteWindow
from gui.history_window import HistoryWindow
from gui.users_management_window import UsersManagementWindow
from gui.search_window import SearchWindow
from gui.stats_window import StatsWindow
from gui.about_window import AboutWindow


class MenuTest(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        self.win = gui.main_window.MainWindow()

    def test_menu_user_managment(self):
        """ Testing user managment opening
        """
        self.connect()
        self.win.user_managment.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            UsersManagementWindow
        )

    def test_menu_change_password(self):
        """ Testing change password opening
        """
        self.win.change_password.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            PasswordManagementWindow
        )

    def test_menu_products_managment(self):
        """ Testing products managment opening
        """
        self.connect()
        self.win.products_managment.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            ProductsManagementWindow
        )

    def test_menu_transaction_history(self):
        """ Testing history opening
        """
        self.win.transaction_history.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            HistoryWindow
        )

    def test_menu_refill_note(self):
        """ Testing refill_note opening
        """
        self.assertFalse(self.win.refill_note.isEnabled())
        self.add_note("coucou")
        self.win.rebuild_notes_list()  # Force the rebuild notes_list.
        self.assertTrue(self.win.refill_note.isEnabled())
        self.connect()
        self.win.refill_note.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            RefillNoteWindow
        )

    def test_menu_empty_note(self):
        """ Testing empty_note opening
        """
        self.assertFalse(self.win.empty_note.isEnabled())
        self.add_note("coucu")
        self.win.rebuild_notes_list()  # Force the rebuild notes_list.
        self.assertTrue(self.win.empty_note.isEnabled())
        self.connect()
        self.win.empty_note.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            EmptyNoteWindow
        )

    def test_menu_manage_notes(self):
        """ Testing manage_notes opening
        """
        self.connect()
        self.win.manage_notes.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            NotesManagementWindow
        )

    def test_menu_notes_action(self):
        """ Testing notes_action opening
        """
        self.connect()
        self.win.notes_action.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            GroupActionsWindow
        )

    def test_menu_find(self):
        """ Testing find opening
        """
        self.connect()
        self.win.find.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            SearchWindow
        )

    def test_menu_panel_managment(self):
        """ Testing panel_managment opening
        """
        self.connect()
        self.win.panel_managment.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            PanelsManagementWindow
        )

    def test_menu_stats_by_note(self):
        """ Testing stats_by_note opening
        """
        self.win.stats_by_note.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            StatsWindow
        )

    def test_menu_stats_by_category(self):
        """ Testing stats_by_category opening
        """
        self.win.stats_by_category.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            StatsWindow
        )

    def test_menu_about(self):
        """ Testing about opening
        """
        self.win.about.trigger()
        self.assertIsInstance(
            self.win.menu_bar.cur_window,
            AboutWindow
        )

