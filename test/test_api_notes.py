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

import basetest
import freezegun
import time
import os.path
import PyQt5
from database import Cursor
import api.notes as notes
import api.redis

api.redis.send_message = lambda x, y: [api.notes.rebuild_note_cache(note) for note in y]


class NotesTest(basetest.BaseTest):
    def setUp(self):
        self._reset_db()
        try:
            os.remove("img/coucou.jpg")
        except FileNotFoundError:
            pass

        try:
            os.remove("img/coucou2.jpg")
        except FileNotFoundError:
            pass
        with Cursor() as cursor:
            cursor.exec_("SET TIMESTAMP=unix_timestamp('2014-12-24 06:00:00')")

    def test_add(self):
        """ Testing adding notes """

        self.assertEqual(notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            True
        ), 1)
        self.assertEqual(notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            True
        ), 2)
        self.assertEqual(notes.add("test2",
            15,
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True,
        ), -1)
        self.assertEqual(self.count_notes(), 2)

    def test_get_by_id(self):
        """ Testing get_by_id """
        id_ = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            False
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
                                 'note': 0.0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': 'coucou.jpg',
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
                                 'mails_inscription': False,
                                 'stats_inscription': True,
                                 'hidden': 0})
        self.assertTrue(os.path.isfile("img/coucou.jpg"))

    def test_get_by_name(self):
        """ Testing get_by_name """
        notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        notes.add("pouette",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )

        res = notes.get(lambda x: 'test' in x["nickname"])
        for i in range(2):
            self.assertIn({'id': i + 1,
                           'nickname': 'test' + str(i),
                           'lastname': 'test',
                           'firstname': 'test',
                           'mail': 'test@pouette.com',
                           'tel': '0600000000',
                           'birthdate': 1008111600,
                           'promo': '1A',
                           'note': 0.0,
                           'overdraft_date': PyQt5.QtCore.QDate(),
                           'ecocups': 0,
                           'photo_path': '',
                           'tot_cons': 0.0,
                           'tot_refill': 0.0,
                           'mails_inscription': True,
                           'stats_inscription': True,
                           'hidden': 0}, res)

    @freezegun.freeze_time("2014-12-24 06:00:00")
    def test_get_by_minors(self):
        """ Testing get minors """
        notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "24/12/1995",
            '1A',
            '',
            True,
            True
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "24/12/1997",
            '1A',
            '',
            True,
            True
        )

        self.assertEqual(notes.get(lambda x: x["birthdate"] > 851403600), [{'id': id1,
                                 'nickname': 'test1',
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 882918000,
                                 'promo': '1A',
                                 'note': 0.0,
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'mails_inscription': True,
                                 'stats_inscription': True,
                                 'hidden': 0}])

    @freezegun.freeze_time("2014-12-24 06:00:00")
    def test_get_by_majors(self):
        """ Testing get majors """
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "24/12/1995",
            '1A',
            '',
            True,
            True
        )
        notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "24/12/1997",
            '1A',
            '',
            True,
            True
        )

        self.assertEqual(notes.get(lambda x: x["birthdate"] < 851403600), [{'id': id0,
                                 'nickname': 'test0',
                                 'lastname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 819759600,
                                 'promo': '1A',
                                 'note': 0.0,
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'mails_inscription': True,
                                 'stats_inscription': True,
                                 'hidden': 0}])

    def test_transaction_multiple(self):
        """ Testing transactions
        """

        self.add_note("test0")
        self.add_note("test1")

        notes.transactions(['test0', 'test1'], 10)
        for note in notes.get():
            self.assertEqual(note['note'], 10)
        notes.transactions(['test0', 'test1'], 10)
        for note in notes.get():
            self.assertEqual(note['note'], 20)
        notes.transactions(['test0', 'test1'], -5)
        for note in notes.get():
            self.assertEqual(note['note'], 15)
        notes.transactions(['test0', 'test1'], -15)
        for note in notes.get():
            self.assertEqual(note['note'], 0)
        notes.transactions(['test0', 'test1'], 5)
        notes.transactions(['test0', 'test1'], -4.95)
        for note in notes.get():
            self.assertEqual(note['note'], 0.05)

    @freezegun.freeze_time("2014-12-24")
    def test_export_xml(self):
        """ Testing notes exporting """
        notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        notes.add("test2",
            "test2",
            "test2",
            "test2@pouette.com",
            "0700000000",
            '12/12/2001',
            '2A',
            '',
            True,
            True
        )
        notes.transactions(["test1", ], -60)
        xml = "<?xml version=\"1.0\"?>\n"
        xml += "<notes date=\"2014-12-24\">\n"
        xml += "\t<note id=\"2\">\n"
        xml += "\t\t<prenom>test2</prenom>\n"
        xml += "\t\t<nom>test2</nom>\n"
        xml += "\t\t<compte>0.0</compte>\n"
        xml += "\t\t<mail>test2</mail>\n"
        xml += "\t\t<date_Decouvert></date_Decouvert>\n"
        xml += "\t</note>\n"
        xml += "\t<note id=\"1\">\n"
        xml += "\t\t<prenom>test</prenom>\n"
        xml += "\t\t<nom>test</nom>\n"
        xml += "\t\t<compte>-60.0</compte>\n"
        xml += "\t\t<mail>test</mail>\n"
        xml += "\t\t<date_Decouvert>2014-12-24</date_Decouvert>\n"
        xml += "\t</note>\n"
        xml += "</notes>\n"
        ex = notes.export(notes.get(), xml=True)
        for line in xml.split():
            self.assertIn(line, ex)

    def test_export_csv(self):
        """ Testing csv export
        """
        notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )

        to_export = ["nickname", "firstname", "lastname", "note", "mail",
                     "photo_path"]
        note = notes.get()[0]
        csv = ", ".join(to_export)
        csv += "\n" + ",".join(str(note[value]) for value in to_export)
        self.assertEqual(csv, notes.export(notes.get(), csv=True))

    def test_export_by_id(self):
        notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        to_export = ["nickname", "firstname", "lastname", "note", "mail",
                     "photo_path"]
        note = notes.get(lambda x: x['nickname'] == "test0")[0]
        csv = ", ".join(to_export)
        csv += "\n" + ",".join(str(note[value]) for value in to_export)
        self.assertEqual(csv, notes.export_by_nick(list(["test0"]), csv=True))

    def test_remove(self):
        """ Testing multiple removing
        """
        self.add_note("test0")
        self.add_note("test1")

        self.assertEqual(self.count_notes(), 2)
        notes.remove(["test0", "test1"])
        self.assertEqual(self.count_notes(), 0)

    def test_modif_note(self):
        """ Testing modifying a note.
        """
        notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "01/01/1994",
            '1A',
            '',
            True,
            True
        )

        notes.change_values("test0", tel="0200000000", promo="3A")
        note = notes.get()[0]
        self.assertEqual(note["tel"], "0200000000")
        self.assertEqual(note["promo"], "3A")

    def test_overdraft(self):
        """ Testing overdraft support
        """
        self.add_note("test0")
        note = notes.get()[0]
        self.assertEqual(note['overdraft_date'], PyQt5.QtCore.QDate())

        notes.transactions(["test0", ], -1)
        note = notes.get()[0]
        now = PyQt5.QtCore.QDateTime(PyQt5.QtCore.QDate(2014, 12, 24))
        self.assertEqual(note['overdraft_date'], now.date())

        notes.transactions(["test0", ], 1)
        note = notes.get()[0]
        self.assertEqual(note['overdraft_date'], PyQt5.QtCore.QDate())

    def test_unique_file_name(self):
        """ Testing get_unique_file_name
        """
        self.assertNotEqual(notes.unique_file("img/a"), notes.unique_file("img/a"))

    def test_change_photo(self):
        """ Testing change_photo
        """
        self.add_note("test0")

        notes.change_photo("test0", "../test/resources/coucou2.jpg")
        note = notes.get()[0]
        self.assertEqual(note['photo_path'], "coucou2.jpg")
        notes.change_photo("test0", "../test/resources/coucou.jpg")
        note = notes.get()[0]
        self.assertEqual(note['photo_path'], "coucou.jpg")
        notes.change_photo("test0", "../test/resources/coucou2.jpg")
        note = notes.get()[0]
        self.assertIn("coucou2", note['photo_path'])
        self.assertNotEqual("coucou2.jpg", note['photo_path'])

    def test_hide_show(self):
        """ Testing show and hide
        """
        self.add_note("test0")
        self.add_note("test1")
        self.add_note("test2")

        for note in notes.get():
            self.assertFalse(bool(note['hidden']))
        notes.hide(["test0", "test1", "test2"])
        for note in notes.get():
            self.assertTrue(bool(note['hidden']))
        notes.show(["test0", "test1", "test2"])
        for note in notes.get():
            self.assertFalse(bool(note['hidden']))

    def test_change_ecocups(self):
        """ Testing change_ecocups
        """
        self.add_note("test0")
        notes.change_ecocups("test0", 5)
        note = notes.get()[0]
        self.assertEqual(note['ecocups'], 5)
        notes.change_ecocups("test0", -3)
        note = notes.get()[0]
        self.assertEqual(note['ecocups'], 2)

    def test_import_csv(self):
        """ Testing import_csv
        """
        self.add_note("test")
        self.add_note("test2")
        self.assertEqual(notes.import_csv(["test", ], "couocu", -2.5), 1)
        self.assertEqual(notes.get(lambda x: x['nickname'] == "test")[0]['note'], -2.5)
        self.assertEqual(notes.get(lambda x: x['nickname'] == "test2")[0]['note'], 0)

    def test_do_not(self):
        """ Testing do_not arg.
        """
        self.add_note("test")
        notes.transactions(['test'], 10, do_not=True)
        self.assertEqual(notes.get()[0]['note'], 0)
        notes.rebuild_cache()
        self.assertEqual(notes.get()[0]['note'], 10)

