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

import api.note_categories as note_categories
import api.notes as notes


class NoteCategoriesTest(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        self.note0 = notes.add("test0",
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
        self.note1 = notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            True
        )
        self.note2 = notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            True
        )
        notes.rebuild_cache()

    def test_get_note_category(self):
        note_categories.add("test")
        note_categories.add("test2")

        self.assertEqual(list(note_categories.get()), [{'name': 'test', 'hidden': 0, 'id': 1}, {'name': 'test2', 'hidden': 0, 'id': 2}])

    def test_add_note_category(self):
        self.assertEqual(note_categories.add("test"), 1)
        self.assertEqual(note_categories.add("test2"), 2)
        self.assertEqual(note_categories.add("test2"), None)

    def test_remove_note_category(self):
        note_categories.add("test1")
        note_categories.add("test2")
        note_categories.add("test3")
        self.assertEqual(self.count_note_categories(), 3)
        note_categories.delete(["test1"])
        self.assertEqual(self.count_note_categories(), 2)
        note_categories.delete(["test2", "test3"])
        self.assertEqual(self.count_note_categories(), 0)

    def test_get_notes_in_note_category(self):
        note_categories.add("test")
        note_categories.add("test2")
        note_categories.add_notes(["test1", "test2"], "test")
        note_categories.add_notes(["test1"], "test2")
        self.assertEqual(list(note_categories.get_notes("test")), ["test1", "test2"])
        self.assertEqual(list(notes.get(lambda x: x['nickname'] == "test1"))[0]['categories'], ["test", "test2"])
        self.assertEqual(list(notes.get(lambda x: x['nickname'] == "test2"))[0]['categories'], ["test"])

    def test_add_notes_to_note_category(self):
        note_categories.add("test")
        self.assertTrue(note_categories.add_notes(["test1", "test2"], "test"))
        self.assertFalse(note_categories.add_notes(["test1"], "test"))
        self.assertFalse(note_categories.add_notes(["test3"], "test"))

    def test_remove_notes_from_note_category(self):
        note_categories.add("test")
        note_categories.add_notes(["test1", "test2"], "test")
        self.assertTrue(note_categories.remove_notes(["test1", "test2"], "test"))
        self.assertEqual(list(note_categories.get_notes("test")), [])

    def test_rename_note_category(self):
        note_categories.add("test")
        note_categories.rename("test", "test_rename")
        self.assertEqual(list(note_categories.get()), [{'name': 'test_rename', 'hidden': 0, 'id': 1}])

    def test_set_hidden_note_category(self):
        note_categories.add("test")
        self.assertEqual(list(note_categories.get()), [{'name': 'test', 'hidden': 0, 'id': 1}])
        note_categories.set_hidden(["test", ], True)
        self.assertEqual(list(note_categories.get()), [{'name': 'test', 'hidden': 1, 'id': 1}])
        note_categories.set_hidden(["test", ], False)
        self.assertEqual(list(note_categories.get()), [{'name': 'test', 'hidden': 0, 'id': 1}])

