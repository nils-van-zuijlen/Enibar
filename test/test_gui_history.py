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


from PyQt5 import QtCore, QtWidgets
import asyncio
import basetest
import gui.history_window
import api.transactions
import api.notes
import api.redis
import json
from freezegun import freeze_time
from database import Cursor


class HistoryWindowTest(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(api.redis.connect())
        api.notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        api.notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        with Cursor() as cursor:
            cursor.exec_("SET TIMESTAMP=unix_timestamp('2015-11-20 21:36:22')")

        api.transactions.log_transactions([{'note': "test1",
                                        'category': "a",
                                        'product': "b",
                                        'price_name': "c",
                                        'quantity': 1,
                                        'price': -1},
                                       {'note': "test1",
                                        'category': "b",
                                        'product': "d",
                                        'price_name': "c",
                                        'quantity': 2,
                                        'price': -5},
                                       {'note': "test2",
                                        'category': "e",
                                        'product': "f",
                                        'price_name': "g",
                                        'quantity': 2,
                                        'price': 5}])
        gui.history_window.HistoryWindow._instance_count = 0
        self.win = gui.history_window.HistoryWindow(parent=None)
        api.notes.rebuild_cache()

    @freeze_time("2015-11-20 21:36:22")
    def test_show_lines(self):
        """ Testing showing history
        """
        def test_func():
            self.assertCountEqual(self.get_tree(self.win.transaction_list),
                [{('2015/11/20 21:36:22', 'test1', 'a', 'b', 'c', '1', '-', '1.0', '1'): []}, {('2015/11/20 21:36:22', 'test1', 'b', 'd', 'c', '2', '-', '5.0', '2'): []}, {('2015/11/20 21:36:22', 'test2', 'e', 'f', 'g', '2', '5.0', '-', '3'): []}]
            )
            self.app.exit()

        QtCore.QTimer.singleShot(2000, test_func)
        self.app.exec_()

    def test_delete_one(self):
        """ Testing deleting one item of history
        """
        async def test_func():
            async with api.redis.connection.get() as redis:
                redis.delete(api.sde.QUEUE_NAME)

                item = self.win.transaction_list.topLevelItem(1)
                self.win.transaction_list.setCurrentItem(item)
                QtCore.QTimer.singleShot(100, self.connect)
                self.win.delete_button.click()
                async def retest_func():
                    res = await redis.blpop(api.sde.QUEUE_NAME)
                    self.assertEqual(json.loads(res[1].decode()), {'token': 'changeme', 'type': 'history', 'price': -2.5, 'id': 2, 'quantity': 1})
                    redis.delete(api.sde.QUEUE_NAME)

                    self.assertEqual(self.get_tree(self.win.transaction_list),
                        [{('2015/11/20 21:36:22', 'test1', 'a', 'b', 'c', '1', '-', '1.0', '1'): []}, {('2015/11/20 21:36:22', 'test1', 'b', 'd', 'c', '1', '-', '2.5', '2'): []}, {('2015/11/20 21:36:22', 'test2', 'e', 'f', 'g', '2', '5.0', '-', '3'): []}]
                    )
                    QtCore.QTimer.singleShot(100, self.connect)
                    self.win.delete_button.click()
                    async def final_func():
                        res = await redis.blpop(api.sde.QUEUE_NAME)
                        self.assertEqual(json.loads(res[1].decode()), {'token': 'changeme', 'type': 'history-delete', 'id': 2})
                        self.assertEqual(self.get_tree(self.win.transaction_list),
                            [{('2015/11/20 21:36:22', 'test1', 'a', 'b', 'c', '1', '-', '1.0', '1'): []}, {('2015/11/20 21:36:22', 'test2', 'e', 'f', 'g', '2', '5.0', '-', '3'): []}]
                        )
                        self.app.exit()
                    task = asyncio.ensure_future(final_func())
                    QtCore.QTimer.singleShot(1000, lambda: self.loop.run_until_complete(task))
            task = asyncio.ensure_future(retest_func())
            QtCore.QTimer.singleShot(1000, lambda: self.loop.run_until_complete(task))
        task = asyncio.ensure_future(test_func())
        QtCore.QTimer.singleShot(1000, lambda: self.loop.run_until_complete(task))
        self.app.exec_()

    def test_delete_line(self):
        """ Testing deleting one line of history
        """
        async def test_func():
            async def final_func():
                res = await redis.blpop(api.sde.QUEUE_NAME)
                self.assertEqual(json.loads(res[1].decode()), {'token': 'changeme', 'type': 'history-delete', 'id': 2})
                self.assertEqual(self.get_tree(self.win.transaction_list),
                    [{('2015/11/20 21:36:22', 'test1', 'a', 'b', 'c', '1', '-', '1.0', '1'): []}, {('2015/11/20 21:36:22', 'test2', 'e', 'f', 'g', '2', '5.0', '-', '3'): []}]
                )
                self.app.exit()
            async with api.redis.connection.get() as redis:
                redis.delete(api.sde.QUEUE_NAME)

                item = self.win.transaction_list.topLevelItem(1)
                self.win.transaction_list.setCurrentItem(item)
                QtCore.QTimer.singleShot(100, self.connect)
                self.win.delete_line_button.click()

                task = asyncio.ensure_future(final_func())
                QtCore.QTimer.singleShot(1000, lambda: self.loop.run_until_complete(task))
        task = asyncio.ensure_future(test_func())
        QtCore.QTimer.singleShot(2000, lambda: self.loop.run_until_complete(task))
        self.app.exec_()

