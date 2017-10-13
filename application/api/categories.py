# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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
Categories
==========

This api handle category managment.

"""

import api.base
import rapi


def add(name):
    """ Add category

    :param str name: Category name
    :return int: Category id
    """
    return rapi.categories.add(name)


def set_alcoholic(cat_id, is_alcoholic):
    """ Set alcoholic state of a product

    :param int cat_id: Category id
    :param bool is_alcoholic: True if categorie products contain alcohol
    """
    return rapi.categories.set_alcoholic(cat_id, is_alcoholic)


def set_color(name, color):
    """ Set category color

    :param str name: Category name
    :param bool: True if operation succed or False
    """
    return rapi.categories.set_color(name, color)


def rename(oldname, newname):
    """ Rename category

    :param str oldname: Old category name
    :param str newname: New category name
    """
    return rapi.categories.rename(oldname, newname)


def remove(name):
    """ Remove category

    :param str name: Category name
    :return bool: True if operation succeed or False
    """
    return rapi.categories.remove(name)


def get(**filter_):
    """ Get category with given values

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("categories", filter_)
    while cursor.next():
        yield {
            'id': cursor.value('id'),
            'name': cursor.value('name'),
            'alcoholic': cursor.value('alcoholic'),
            'color': cursor.value('color'),
        }


get_unique = api.base.make_get_unique(get)

