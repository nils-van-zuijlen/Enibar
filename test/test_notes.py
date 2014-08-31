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

import basetest
import datetime
import unittest
import time
import os.path
import PyQt5
import api.notes as notes
from database import Cursor


class NotesTest(unittest.TestCase):
    def setUp(self):
        with Cursor() as cursor:
            cursor.exec("TRUNCATE TABLE notes")

    def count_notes(self):
        """ Returns the number of notes currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM notes")
            if cursor.next():
                return cursor.record().value(0)

    def test_add(self):
        """ Testing adding notes """

        self.assertEqual(notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        ), 1)
        self.assertEqual(notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        ), 2)
        self.assertEqual(notes.add("test2",
            15,
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        ), -1)
        self.assertEqual(self.count_notes(), 2)

    def test_remove(self):
        """ Testing removing notes """
        id_ = notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )

        self.assertTrue(notes.remove(id_))
        self.assertEqual(self.count_notes(), 0)

    def test_get_by_id(self):
        """ Testing get_by_id """
        id_ = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg'
        )
        getted = notes.get(lambda x: x['id'] == id_)[0]
        self.assertEqual(getted, {'id': id_,
                                 'nickname': 'test1',
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 1008111600,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': 'coucou.jpg',
                                 'hidden': 0})
        self.assertTrue(os.path.isfile("img/coucou.jpg"))

    def test_get_by_name(self):
        """ Testing get_by_name """
        id1 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        id2 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        id3 = notes.add("pouette",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )

        self.assertEqual(notes.get(lambda x: 'test' in x["nickname"]), [{'id': i + 1,
                                 'nickname': 'test' + str(i),
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 1008111600,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0} for i in range(2)])

    def test_get_by_minors(self):
        """ Testing get minors """
        time0 = round(time.time() - 19 * 365 * 24 * 3600)
        time1 = round(time.time() - 17 * 365 * 24 * 3600)
        dt1 = int(datetime.datetime.fromtimestamp(time1).replace(hour=0, minute=0, second=0).timestamp())
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            datetime.datetime.fromtimestamp(time0).strftime("%d/%m/%Y"),
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            datetime.datetime.fromtimestamp(time1).strftime("%d/%m/%Y"),
            '1A',
            ''
        )

        self.assertEqual(notes.get(lambda x: x["birthdate"] > time.time() - 18 * 365 * 24 * 3600), [{'id': id1,
                                 'nickname': 'test1',
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': dt1,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0}])

    def test_get_by_majors(self):
        """ Testing get majors """
        time0 = round(time.time() - 19 * 365 * 24 * 3600)
        time1 = round(time.time() - 17 * 365 * 24 * 3600)
        dt0 = int(datetime.datetime.fromtimestamp(time0).replace(hour=0, minute=0, second=0).timestamp())
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            datetime.datetime.fromtimestamp(time0).strftime("%d/%m/%Y"),
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            datetime.datetime.fromtimestamp(time1).strftime("%d/%m/%Y"),
            '1A',
            ''
        )

        self.assertEqual(notes.get(lambda x: x["birthdate"] < time.time() - 18 * 365 * 24 * 3600), [{'id': id0,
                                 'nickname': 'test0',
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': dt0,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0}])

    def test_transaction(self):
        """ Testing transactions """
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )

        notes.transaction("test1", 10)
        self.assertEqual(notes.get(lambda x: x["nickname"] == "test1")[0]['note'], 10)
        notes.transaction("test1", 10)
        self.assertEqual(notes.get(lambda x: x["nickname"] == "test1")[0]['note'], 20)
        notes.transaction("test1", -5)
        self.assertEqual(notes.get(lambda x: x["nickname"] == "test1")[0]['note'], 15)
        notes.transaction("test1", -15)
        self.assertEqual(notes.get(lambda x: x["nickname"] == "test1")[0]['note'], 0)
        notes.transaction("test1", 5)
        notes.transaction("test1", -4.95)
        self.assertEqual(notes.get(lambda x: x["nickname"] == "test1")[0]['note'], 0.05)

    def test_export_xml(self):
        """ Testing notes exporting """
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        xml = "<?xml version=\"1.0\"?>\n"
        xml += "<notes date=\"{}\">\n".format(datetime.datetime.now().strftime(
            "%Y-%m-%d"))
        xml += "\t<note id=\"1\">\n"
        xml += "\t\t<prenom>test</prenom>\n"
        xml += "\t\t<nom>test</nom>\n"
        xml += "\t\t<compte>0.0</compte>\n"
        xml += "\t\t<image></image>\n"
        xml += "\t\t<date_Decouvert></date_Decouvert>\n"
        xml += "\t</note>\n"
        xml += "</notes>\n"
        self.assertEqual(notes.export(notes.get(), xml=True), xml)

    def test_remove_multiple(self):
        """ Testing multiple removing
        """
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "01/01/1994",
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "01/01/1994",
            '1A',
            ''
        )

        self.assertEqual(self.count_notes(), 2)
        notes.remove_multiple([id0, id1])
        self.assertEqual(self.count_notes(), 0)

    def test_modif_note(self):
        """ Testing modifying a note.
        """
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "01/01/1994",
            '1A',
            ''
        )

        notes.change_values("test0", tel="0200000000", promo="3A")
        note = list(notes.get())[0]
        self.assertEqual(note["tel"], "0200000000")
        self.assertEqual(note["promo"], "3A")

    def test_overdraft(self):
        """ Testing overdraft support
        """
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "01/01/1994",
            '1A',
            ''
        )
        note = list(notes.get())[0]
        self.assertEqual(note['overdraft_date'], PyQt5.QtCore.QDate())

        notes.transaction("test0", -1)
        note = list(notes.get())[0]
        now = PyQt5.QtCore.QDateTime()
        now.setMSecsSinceEpoch(time.time() * 1000)
        self.assertEqual(note['overdraft_date'], now.date())

        notes.transaction("test0", 1)
        note = list(notes.get())[0]
        self.assertEqual(note['overdraft_date'], PyQt5.QtCore.QDate())


