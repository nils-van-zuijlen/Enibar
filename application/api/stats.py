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
Stats
=====

This api provides some neat stats.
"""

from database import Cursor

STATS_FIELDS = ['nickname', 'product', 'price_name', 'price', 'category', 'quantity']
STATS_FIELDS_CACHE = {}


def get_notes_stats():
    """ Yield dicts representing stats.

        {'nickname', 'product', 'price_name', 'price', 'category', 'quantity'}
    """
    global STATS_FIELDS_CACHE
    with Cursor() as cursor:
        cursor.prepare("SELECT notes.nickname AS nickname,\
                        transactions.product AS product,\
                        transactions.price_name AS price_name,\
                        transactions.price/transactions.quantity AS price,\
                        transactions.category AS category,\
                        SUM(transactions.quantity) AS quantity \
                        FROM transactions JOIN notes ON \
                        ((notes.lastname = transactions.lastname AND \
                        notes.firstname = transactions.firstname) OR \
                        notes.nickname = transactions.note) AND \
                        notes.stats_inscription = TRUE \
                        GROUP BY notes.nickname, transactions.product,\
                        transactions.price_name, transactions.price, \
                        transactions.quantity, transactions.category")
        cursor.exec_()
        while cursor.next():
            if not STATS_FIELDS_CACHE:
                STATS_FIELDS_CACHE = {field: cursor.indexOf(field) for field in STATS_FIELDS}

            yield {field: cursor.value(STATS_FIELDS_CACHE[field]) for field in STATS_FIELDS}


def get_red_sum():
    with Cursor() as cursor:
        cursor.prepare(
            "SELECT COUNT(*) as nb_notes, SUM(note) AS red"
            "FROM notes WHERE note < 0 AND stats_inscription=TRUE")
        cursor.exec_()
        if cursor.next():
            return cursor.value('nb_notes'), cursor.value('red')


def get_green_sum():
    with Cursor() as cursor:
        cursor.prepare(
            "SELECT COUNT(*) as nb_notes, SUM(note) AS green"
            "FROM notes WHERE note > 0 AND stats_inscription=TRUE")
        cursor.exec_()
        if cursor.next():
            return cursor.value('nb_notes'), cursor.value('green')


def get_red_notes():
    with Cursor() as cursor:
        cursor.prepare(
            "SELECT nickname, note FROM notes"
            "WHERE note < 0 AND stats_inscription=TRUE ORDER BY note")
        cursor.exec_()
        while cursor.next():
            yield cursor.value('nickname'), cursor.value('note')


def get_ecocups_nb():
    with Cursor() as cursor:
        cursor.prepare("SELECT SUM(ecocups) AS nb_ecocups FROM notes")
        cursor.exec_()
        if cursor.next():
            return cursor.value("nb_ecocups")

