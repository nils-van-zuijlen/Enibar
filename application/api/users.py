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
Users
=====

"""

import api.base
import rapi

RIGHTS = ['manage_users', 'manage_notes', 'manage_products']


def add(username, password):
    """ Add an admin.

    :param str username: Username
    :param str password: Password

    :return bool: True if success else False.
    """
    return rapi.users.add(username, password)


def remove(username):
    """ Remove an admin.

    :param str username: Admin username

    :return bool: True if success else False.
    """
    return rapi.users.remove(username)


def get_list(**filter_):
    """ Get user list

    :return list: list of users name
    """
    if any(right not in RIGHTS for right in filter_):
        return

    cursor = api.base.filtered_getter("admins", filter_, order_by="login")
    while cursor.next():
        yield cursor.value('login')


def get_rights(username):
    """ Get user rights

    :return dict: rights for given username
    """
    return rapi.users.get_rights(username)


def set_rights(username, rights):
    """ Set user rights

    :param str username: The username
    :param dict rights: A dict that contains the rights. example:\
    ``{'manage_users': True,
     'manage_notes': False,
     'manage_products': True}``

    :return bool: Operation status
    """
    return rapi.users.set_rights(username, rights)


def change_password(username, new_password):
    """ Change password of an admin.

    :param str username: Admin username
    :param str new_password: New password

    :return bool: True if success else False.
    """
    return rapi.users.change_password(username, new_password)


def is_authorized(username, password):
    """ Check if a combination of username/password match an admin in database.

    :param str username: username
    :param str password: Password

    :return bool: True if authorized else False.
    """
    return rapi.users.is_authorized(username, password)
