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
Base api, with common functions.
"""

from database import Cursor


def make_get_unique(getter):
    """ Make get_unique function for apis
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


def filtered_getter(table):
    """ Filtered getter
    Used to build filter around getters.
    This is advanced stuff be sure you fully understand decorators before you
    even remotly think about editing this.
    Deal with it
    """
    def decorator(func):
        """ Decorator
        """
        def wrapper(**kwargs):
            """ Wrapper
            """
            with Cursor() as cursor:
                filters = []
                for key in kwargs:
                    filters.append("{key}=:{key}".format(key=key))
                cursor.prepare("SELECT * FROM {} {} {}".format(
                    table,
                    "WHERE" * bool(len(filters)),
                    " AND ".join(filters)
                ))
                for key, arg in kwargs.items():
                    cursor.bindValue(":{}".format(key), arg)
                if cursor.exec_():
                    yield from func(cursor=cursor)
        return wrapper
    return decorator
