# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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
Stats
=====

This api provides some neat stats.
"""

from database import Cursor


def get_notes_stats():
    """ Yield dicts representing stats.

        {'nickname', 'product', 'price_name', 'price', 'category', 'quantity'}
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT notes.nickname AS nickname,\
                        transactions.product AS product,\
                        transactions.price_name AS price_name,\
                        transactions.price/quantity AS price,\
                        transactions.category AS category,\
                        SUM(transactions.quantity) AS quantity\
                        FROM transactions INNER JOIN notes WHERE\
                        ((notes.lastname = transactions.lastname AND\
                        notes.firstname = transactions.firstname) OR\
                        notes.nickname = transactions.note) AND\
                        notes.stats_inscription = TRUE\
                        GROUP BY notes.nickname, transactions.product,\
                        transactions.price_name, transactions.price")
        cursor.exec_()
        while cursor.next():
            record = cursor.record()

            yield {field: record.value(field) for field in (
                'nickname',
                'product',
                'price_name',
                'price',
                'category',
                'quantity')
            }

