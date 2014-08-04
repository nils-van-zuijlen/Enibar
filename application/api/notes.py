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

"""
Notes management functions
==========================

"""

from database import Cursor
import datetime
import os.path
import shutil


NOTE_FIELDS = ['id', 'nickname', 'surname', 'firstname', 'mail', 'tel',
               'birthdate', 'promo', 'note', 'photo_path', 'overdraft_time',
               'ecocups', 'hidden']

NOTES_CACHE = []


def rebuild_cache():
    """ Build a cache with all notes inside. This improve greatly the perfs of
        get actions
    """
    # pylint: disable=global-statement
    global NOTES_CACHE
    NOTES_CACHE = []
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes")
        if cursor.exec_():
            while cursor.next():
                row = {field: cursor.record().value(field) for field in
                       NOTE_FIELDS}
                NOTES_CACHE.append(row)
    return True


# pylint: disable=too-many-arguments
def add(nickname, surname, firstname, mail, tel, birthdate, promo, photo_path):
    """ Create a note. Copy the image from photo_path to img/

    :param str nickname: Nickname
    :param str surname: Surname
    :param str firstname: First name
    :param str mail: Mail
    :param str tel: Phone number
    :param int birthdate: Birthday (DD/MM/YYYY)
    :param str promo: Promo. One of '1A', '2A', '3A', '3S', '4A', '5A',\
    'Ancien', 'Prof', 'Externe', Esiab'
    :param str photo_path: The path of the photo to use. The root is img/

    :return bool: The id of the note created or -1.
    """
    if photo_path:
        name = os.path.split(photo_path)[1]
        if name:
            shutil.copyfile(photo_path, "img/" + name)

    with Cursor() as cursor:
        cursor.prepare("INSERT INTO notes (nickname, surname, firstname,\
                        mail, tel, birthdate, promo, photo_path)\
                        VALUES(:nickname, :surname, :firstname, :mail, :tel,\
                        :birthdate, :promo, :photo_path)")
        birthdate = datetime.datetime.strptime(birthdate,
                                               "%d/%m/%Y").timestamp()

        cursor.bindValues({':nickname': nickname, ':surname': surname,
                           ':firstname': firstname, ':mail': mail, ':tel': tel,
                           ':birthdate': birthdate, ':promo': promo,
                           ':photo_path': "img/" + name if photo_path else ""})

        if cursor.exec_():
            rebuild_cache()
            return cursor.lastInsertId()
        return -1


def remove(id_):
    """ Remove a note

    :param int id_: The id of the note to delete

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM notes WHERE id=:id")
        cursor.bindValue(':id', id_)
        return cursor.exec_() and rebuild_cache()


def change_nickname(id_, new_nickname):
    """ Change a note nickname.

    :param int id_: The id of the note
    :param str new_nickname: The new nickname

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET nickname=:nickname WHERE id=:id")

        cursor.bindValues({':nickname': new_nickname, ':id': id_})

        return cursor.exec_() and rebuild_cache()


def change_tel(id_, new_tel):
    """ Change a note phone number.

    :param int id_: The id of the note
    :param str new_tel: The new phone number

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET tel=:tel WHERE id=:id")

        cursor.bindValues({':tel': new_tel, ':id': id_})

        return cursor.exec_() and rebuild_cache()


def change_photo(id_, new_photo):
    """ Change a note photo.

    :param int id_: The id of the note
    :param str new_path: The new photo_path

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET photo_path=:photo_path WHERE id=:id")

        cursor.bindValues({':photo_path': new_photo, ':id': id_})

        return cursor.exec_() and rebuild_cache()


def get(filter_=None):
    """ Get notes with a filter. filter_ should be a function like
            lamda x: x["id"] == 1
        to keep only notes with the id 1
    """
    rows = []
    for row in NOTES_CACHE:
        if filter_ is None or filter_(row):
            rows.append(row)
    return rows


def hide(id_):
    """ Hide a note

    :param int id_: The id of the note you want to hide

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET hidden=1 WHERE id=:id")
        cursor.bindValue(':id', id_)
        return cursor.exec_()


def show(id_):
    """ Show a note

    :param int id_: The id of the note you want to show

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET hidden=0 WHERE id=:id")
        cursor.bindValue(':id', id_)
        return cursor.exec_()


def transaction(id_, diff):
    """ Change the note of a note.

    :param int id_: The id of the note
    :param float diff: Will add the diff to the note.

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET note=note+:diff WHERE id=:id")
        cursor.bindValue(":diff", diff)
        cursor.bindValue(":id", id_)

        return cursor.exec_() and rebuild_cache()

rebuild_cache()

