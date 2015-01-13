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

import basetest
import datetime
import time
import os.path
import PyQt5
import api.notes as notes


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

    def test_add(self):
        """ Testing adding notes """

        self.assertEqual(notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg'
        ), 1)
        self.assertEqual(notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg'
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
                                 'note': 0.0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': 'coucou.jpg',
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
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
                                 'note': 0.0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
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
                                 'note': 0.0,
                                 'tot_cons': 0.0,
                                 'tot_refill': 0.0,
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
                                 'note': 0.0,
                                 'tot_cons': 0,
                                 'tot_refill': 0,
                                 'overdraft_date': PyQt5.QtCore.QDate(),
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0}])

    def test_transaction_multiple(self):
        """ Testing transactions
        """

        id0 = self.add_note("test0")
        id1 = self.add_note("test1")

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
        id2 = notes.add("test2",
            "test2",
            "test2",
            "test2@pouette.com",
            "0700000000",
            '12/12/2001',
            '2A',
            ''
        )
        notes.transactions(["test1", ], -60)
        xml = "<?xml version=\"1.0\"?>\n"
        xml += "<notes date=\"{}\">\n".format(datetime.datetime.now().strftime(
            "%Y-%m-%d"))
        xml += "\t<note id=\"1\">\n"
        xml += "\t\t<prenom>test</prenom>\n"
        xml += "\t\t<nom>test</nom>\n"
        xml += "\t\t<compte>-60.0</compte>\n"
        xml += "\t\t<mail>test</mail>\n"
        xml += "\t\t<date_Decouvert>{}</date_Decouvert>\n".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        xml += "\t</note>\n"
        xml += "\t<note id=\"2\">\n"
        xml += "\t\t<prenom>test2</prenom>\n"
        xml += "\t\t<nom>test2</nom>\n"
        xml += "\t\t<compte>0.0</compte>\n"
        xml += "\t\t<mail>test2</mail>\n"
        xml += "\t\t<date_Decouvert></date_Decouvert>\n"
        xml += "\t</note>\n"
        xml += "</notes>\n"
        self.assertEqual(notes.export(notes.get(), xml=True), xml)

    def test_export_csv(self):
        """ Testing csv export
        """
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )

        to_export = ["nickname", "firstname", "lastname", "note", "mail",
                     "photo_path"]
        note = notes.get()[0]
        csv = ", ".join(to_export)
        csv += "\n" + ",".join(str(note[value]) for value in to_export)
        self.assertEqual(csv, notes.export(notes.get(), csv=True))

    def test_export_by_id(self):
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
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
        id0 = self.add_note("test0")
        id1 = self.add_note("test1")

        self.assertEqual(self.count_notes(), 2)
        notes.remove(["test0", "test1"])
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
        note = notes.get()[0]
        self.assertEqual(note["tel"], "0200000000")
        self.assertEqual(note["promo"], "3A")

    def test_overdraft(self):
        """ Testing overdraft support
        """
        id0 = self.add_note("test0")
        note = notes.get()[0]
        self.assertEqual(note['overdraft_date'], PyQt5.QtCore.QDate())

        notes.transactions(["test0", ], -1)
        note = notes.get()[0]
        now = PyQt5.QtCore.QDateTime()
        now.setMSecsSinceEpoch(time.time() * 1000)
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
        id0 = self.add_note("test0")

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
        id0 = self.add_note("test0")
        id1 = self.add_note("test1")
        id2 = self.add_note("test2")

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
        id0 = self.add_note("test0")
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

