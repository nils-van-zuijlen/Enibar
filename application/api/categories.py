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
Categories API
==============

This api handle category managment.

"""

from database import Cursor


def add(name):
    """ Add category

    :param str name: Category name
    :return int: Category id
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO categories(name) VALUES(:name)")
        cursor.bindValue(':name', name)
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


def get_all():
    """ Get all categories without any filter
    Deprecated use get instead

    :return generator: All categories
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM categories")
        cursor.exec_()
        while cursor.next():
            yield {
                'id': cursor.record().value('id'),
                'name': cursor.record().value('name'),
            }


def get_by_name(name):
    """ Get category by name
    deprecated use get_unique instead

    :param str name: Category name
    :return dict: Caterogy description
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM categories WHERE name=:name")
        cursor.bindValue(':name', name)
        cursor.exec_()
        if cursor.next():
            return {
                'id': cursor.record().value('id'),
                'name': cursor.record().value('name'),
            }


def get(**kwargs):
    """ Get category with given values

    :param dict kwargs: filter to apply
    """
    with Cursor() as cursor:
        filters = []
        for key in kwargs:
            filters.append("{key}=:{key}".format(key=key))
        cursor.prepare("SELECT * FROM categories WHERE {filter}".format(
            filter=" AND ".join(filters)
        ))
        for key, value in kwargs.items():
            cursor.bindValue(":{}".format(key), value)
        if cursor.exec_():
            while cursor.next():
                yield {
                    'id': cursor.record().value('id'),
                    'name': cursor.record().value('name'),
                }


def get_unique(**kwargs):
    """ Get categories with filter and return something only if unique

    :param **kwargs: filters
    """
    # pylint: disable=
    results = list(get(**kwargs))
    if len(results) != 1:
        return None
    else:
        return results[0]

