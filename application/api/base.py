# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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
Base api, with common functions.
"""

from database import Cursor


def make_get_unique(getter):
    """ Make get_unique function for apis.
    """
    get = getter

    def get_unique(**kwargs):
        """ Get categories with filter and return something only if unique

        :param **kwargs: filters
        """
        results = list(get(**kwargs))
        if len(results) != 1:
            return None
        else:
            return results[0]
    return get_unique


def filtered_getter(table, filter_, reverse=False, max=None):
    """ This creates a request in the table table with the filter filter_ and
        returns the cursor of this request for future use.
    """
    with Cursor() as cursor:
        filters = []
        for key in filter_:
            filters.append("{key}=:{key}".format(key=key))

        cursor.prepare("SELECT * FROM {} {} {} {} {}".format(
            table,
            "WHERE" * bool(len(filters)),
            " AND ".join(filters),
            "ORDER BY id DESC" * reverse,
            "LIMIT 0, {}".format(max) * bool(max),
        ))
        for key, arg in filter_.items():
            cursor.bindValue(":{}".format(key), arg)
        if cursor.exec_():
            return cursor

