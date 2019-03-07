# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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

"""
Note categories
=====

"""

from database import Cursor
import api.base
import api.notes
import rapi


NOTE_CATEGORY_FIELDS = ['id', 'name', 'hidden', 'protected']
NOTE_CATEGORY_FIELDS_CACHE = {}


def add(name):
    """ Add an empty note category

    :param str name: Note category name
    :return int: Note category id
    """
    return rapi.note_categories.add(name)


def delete(names):
    """ Delete a note category

    :param str name: The name of the category to delete
    """
    return rapi.note_categories.remove(names)


def add_notes(note_names, category_name):
    """ Add notes to the note category

    :param list note_names: A list of nicknames of notes to add to this category
    :param str category_name: The category name

    :return bool: True if the notes have been added, False otherwise
    """
    with Cursor() as cursor:
        cursor.prepare("""
            INSERT INTO note_categories_assoc (note, category)
            VALUES((SELECT id FROM notes WHERE nickname=:note),
                   (SELECT id FROM note_categories WHERE name=:category))
            """)

        cursor.bindValue(':note', note_names)
        cursor.bindValue(':category', [category_name, ] * len(note_names))

        ret = cursor.execBatch()
        if ret:
            for note in note_names:
                api.notes.rebuild_note_cache(note)
            api.redis.send_message("enibar-notes", note_names)
        return ret


def remove_notes(note_names, category_name):
    """ Remove notes from a category

    :param list note_names: A list of nicknames of notes to remove from this category
    :param str category_name: The category name

    :return bool: True if the notes have been removed, False otherwise
    """
    with Cursor() as cursor:
        cursor.prepare("""
            DELETE FROM note_categories_assoc WHERE
                note=(SELECT id FROM notes WHERE nickname=:note) AND
                category=(SELECT id FROM note_categories WHERE name=:category)
            """)

        cursor.bindValue(":note", note_names)
        cursor.bindValue(":category", [category_name, ] * len(note_names))

        ret = cursor.execBatch()
        if ret:
            for note in note_names:
                api.notes.rebuild_note_cache(note)
            api.redis.send_message("enibar-notes", note_names)
        return ret


def get_notes(category_name):
    """ Yields the nicknames of all the notes in the category

    :param str category_name: The category name
    """
    with Cursor() as cursor:
        cursor.prepare("""
            SELECT filtered_notes.nickname as nick FROM
                (SELECT id, nickname FROM notes WHERE notes.id IN
                    (SELECT note FROM note_categories_assoc WHERE category=
                        (SELECT id FROM note_categories WHERE name=:name)
                    )
                ) filtered_notes
            """)

        cursor.bindValue(':name', category_name)

        if cursor.exec_():
            while cursor.next():
                yield cursor.value("nick")


def rename(old_name, new_name):
    """ Rename a note category

    :param str old_name: Old category name
    :param str new_name: New category name

    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE note_categories SET name=:new_name WHERE name=:old_name AND protected=FALSE")

        cursor.bindValue(":new_name", new_name)
        cursor.bindValue(":old_name", old_name)

        cursor.exec_()


def set_hidden(category_names, hidden):
    """ Change the hidden value of one or more categories

    :param str category_name: The name of the category
    :param bool hidden: The new state.
    """
    with Cursor() as cursor:
        cursor.prepare(
            "UPDATE note_categories SET hidden=:hidden WHERE name=:name AND protected=FALSE"
        )

        cursor.bindValue(":name", category_names)
        cursor.bindValue(":hidden", [hidden, ] * len(category_names))

        cursor.execBatch()
    notes = api.notes.get(
        lambda x: any(category_name in x["categories"] for category_name in category_names))
    api.redis.send_message("enibar-notes", [note['nickname'] for note in notes])


def get(**filter_):
    """ Get category with given values

    :param dict filter_: filter to apply
    """
    global NOTE_CATEGORY_FIELDS_CACHE

    cursor = api.base.filtered_getter("note_categories", filter_)
    while cursor.next():
        if NOTE_CATEGORY_FIELDS_CACHE == {}:
            NOTE_CATEGORY_FIELDS_CACHE = {f: cursor.indexOf(f) for f in NOTE_CATEGORY_FIELDS}
        yield {field: cursor.value(NOTE_CATEGORY_FIELDS_CACHE[field]) for field in
               NOTE_CATEGORY_FIELDS}


get_unique = api.base.make_get_unique(get)
