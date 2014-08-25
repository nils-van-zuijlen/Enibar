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

# pylint: disable=invalid-name

"""
Categories API
==============

This api handle category managment.

"""

from database import Cursor
import api.base


def add(name):
    """ Add category

    :param str name: Category name
    :return int: Category id
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO categories(name) VALUES(:cat_name)")
        cursor.bindValue(':cat_name', name)
        if cursor.exec_():
            return cursor.lastInsertId()  # Return the created category
        else:
            return None


def set_alcoholic(cat_id, is_alcoholic):
    """ Set alcoholic state of a product

    :param int cat_id: Category id
    :param bool is_alcoholic: True if categorie products contain alcohol
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE categories SET alcoholic=? WHERE id=?")
        cursor.addBindValue(is_alcoholic)
        cursor.addBindValue(cat_id)
        return cursor.exec_()


def remove(name):
    """ Remove category

    :param str name: Category name
    :return bool: True if operation succeed or False
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM categories WHERE name=:name")
        cursor.bindValue(':name', name)
        return cursor.exec_()


def get(**filter_):
    """ Get category with given values

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("categories", filter_)
    while cursor.next():
        yield {
            'id': cursor.record().value('id'),
            'name': cursor.record().value('name'),
            'alcoholic': cursor.record().value('alcoholic'),
        }


get_unique = api.base.make_get_unique(get)

