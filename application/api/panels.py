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
Panel management functions
==========================

"""

from database import Cursor
import api.base


def add(name):
    """ Add a panel.

    :param str name: The name of the tab.

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO panels(name) VALUES(:name)")
        cursor.bindValue(':name', name)

        return cursor.exec_()


def remove(name):
    """ Remove an panel

    :param str penel: Panel name

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM panels WHERE name=:name")
        cursor.bindValue(':name', name)

        return cursor.exec_()


@api.base.filtered_getter('panels')
def get(cursor):
    """ Get panel with given values

    :param dict kwargs: filter to apply
    """
    while cursor.next():
        yield {
            'name': cursor.record().value('name'),
            'id': cursor.record().value('id'),
        }

# pylint: disable=invalid-name
get_unique = api.base.make_get_unique(get)


