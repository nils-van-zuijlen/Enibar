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
import time


NOTE_FIELDS = ['id', 'nickname', 'surname', 'firstname', 'mail', 'tel',
               'birthdate', 'promo', 'note', 'overdraft_time', 'ecocups',
               'hidden']


# pylint: disable=too-many-arguments
def add(nickname, surname, firstname, mail, tel, birthdate, promo):
    """ Create a note.

    :param str nickname: Nickname
    :param str surname: Surname
    :param str firstname: First name
    :param str mail: Mail
    :param str tel: Phone number
    :param int birthdate: Birthday (timestamp)
    :param str promo: Promo. One of '1A', '2A', '3A', '3S', '4A', '5A',\
    'Ancien', 'Prof'

    :return bool: The id of the note created or -1.
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO notes (nickname, surname, firstname,\
                        mail, tel, birthdate, promo)\
                        VALUES(:nickname, :surname, :firstname, :mail, :tel,\
                        :birthdate, :promo)")

        cursor.bindValues({':nickname': nickname, ':surname': surname,
                           ':firstname': firstname, ':mail': mail, ':tel': tel,
                           ':birthdate': birthdate, ':promo': promo})

        if cursor.exec_():
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
        return cursor.exec_()


def change_nickname(id_, new_nickname):
    """ Change a note nickname.

    :param int id_: The id of the note
    :param str new_nickname: The new nickname

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET nickname=:nickname WHERE id=:id")

        cursor.bindValues({':nickname': new_nickname, ':id': id_})

        return cursor.exec_()


def change_tel(id_, new_tel):
    """ Change a note phone number.

    :param int id_: The id of the note
    :param str new_tel: The new phone number

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET tel=:tel WHERE id=:id")

        cursor.bindValues({':tel': new_tel, ':id': id_})

        return cursor.exec_()


def get_by_id(id_):
    """ Get note by id

    :param int id_: The id of the note

    :return dict: Description of the note or None if not found
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE id=:id")

        cursor.bindValue(":id", id_)

        cursor.exec_()
        if cursor.next():
            return {field: cursor.record().value(field) for field in
                    NOTE_FIELDS}
        else:
            return None


def get_by_nickname(nickname):
    """ Get notes by nickname

    :param str nickname: The nickname you want to search

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE nickname LIKE :nickname")

        cursor.bindValue(':nickname', "%{}%".format(nickname))

        cursor.exec_()
        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_by_first_name(firstname):
    """ Get notes by first name

    :param str firstname: The first name you want to search

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE firstname LIKE :firstname")

        cursor.bindValue(':firstname', "%{}%".format(firstname))

        cursor.exec_()
        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_by_surname(surname):
    """ Get notes by surname

    :param str surname: The surname you want to search

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE surname LIKE :surname")

        cursor.bindValue(':surname', "%{}%".format(surname))
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_by_promo(promo):
    """ Get notes by promo

    :param str promo: The promo you want to search

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE promo LIKE :promo")

        cursor.bindValue(':promo', "%{}%".format(promo))
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_minors():
    """ Get minors notes

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE birthdate+567648000 > :time")
        cursor.bindValue(':time', time.time())
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_majors():
    """ Get majors notes

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE birthdate+567648000 <= :time")
        cursor.bindValue(':time', time.time())
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


def get_profs():
    """ Get profs notes

    :return list: List of note descriptions
    """
    with Cursor() as cursor:
        cursor.exec("SELECT * FROM notes WHERE promo=Profs")

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   NOTE_FIELDS}


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

