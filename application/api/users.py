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
Admin management functions
==========================

"""

import bcrypt
from database import Cursor


def add(pseudo, password):
    """ Add an admin.

    :param str pseudo: Pseudo
    :param str password: Password

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO admins VALUES(:login, :pass, 0, 0, 0)")
        cursor.bindValue(':login', pseudo)
        cursor.bindValue(':pass', bcrypt.hashpw(password,
                                                bcrypt.gensalt()))

        return cursor.exec_()


def remove(pseudo):
    """ Remove an admin.

    :param str pseudo: Admin pseudo

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM admins WHERE login=:pseudo")
        cursor.bindValue(':pseudo', pseudo)

        return cursor.exec_()


def get_list():
    """ Get user list

    :return list: list of users name
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT login FROM admins")
        cursor.exec_()
        while cursor.next():
            yield cursor.record().value('login')


def get_rights(username):
    """ Get user rights

    :return dict: rights for given username
    """
    with Cursor() as cursor:
        cursor.prepare("""SELECT
            manage_users,
            manage_notes,
            manage_products
            FROM admins WHERE login=:login
            """)
        cursor.bindValue(':login', username)
        if cursor.exec_() and cursor.next():
            return {
                'manage_users': cursor.record().value('manage_users'),
                'manage_notes': cursor.record().value('manage_notes'),
                'manage_products': cursor.record().value('manage_products'),
            }
        else:
            return {
                'manage_users': False,
                'manage_notes': False,
                'manage_products': False,
            }


def set_rights(username, rights):
    """ Set user rights

    :return bool: Operation status
    """
    with Cursor() as cursor:
        cursor.prepare("""UPDATE admins
            SET manage_users=:manage_users,
            manage_notes=:manage_notes,
            manage_products=:manage_products
            WHERE login=:login
            """)
        for right, value in rights.items():
            cursor.bindValue(':{}'.format(right), value)
        cursor.bindValue(':login', username)
        return cursor.exec_()


def change_password(pseudo, new_password):
    """ Change password of an admin.

    :param str pseudo: Admin pseudo
    :param str new_password: New password

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE admins SET password=:pass WHERE login=:login")
        cursor.bindValue(':login', pseudo)
        cursor.bindValue(':pass', bcrypt.hashpw(new_password,
                                                bcrypt.gensalt()))

        return cursor.exec_()


def is_authorized(pseudo, password):
    """ Check if a combination of pseudo/password match an admin in database.

    :param str pseudo: Pseudo
    :param str password: Password

    :return bool: True if authorized else False.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT password FROM admins WHERE login=:login")
        cursor.bindValue(':login', pseudo)
        if not cursor.exec_():
            return False

        if not cursor.record().count():
            return False

        if not cursor.next():
            return False

        hashed = cursor.record().value("password")
        return bcrypt.hashpw(password, hashed) == hashed

