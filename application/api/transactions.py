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
Transactions
============

Provide usefull api to interact with transaction hisotry and log, every
consumption bought.
"""

from PyQt5 import QtSql
from database import Database, Cursor
import asyncio
import api.base
import api.notes
import api.sde
import datetime


def log_transactions(transactions, do_not=False):
    """ Log multiple transactions

    :param list transactions:
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("""INSERT INTO transactions(
                date, note, category, product, price_name,
                quantity, price, firstname, lastname, liquid_quantity,
                percentage, deletable, note_id
            )
            VALUES(
                NOW(), :note, :category, :product, :price_name,
                :quantity, :price, :firstname, :lastname, :liquid_quantity,
                :percentage, :deletable, :note_id
            )""")
        now = datetime.datetime.now().isoformat()
        for trans in transactions:
            notes = api.notes.get(lambda x: x['nickname'] == trans['note'])
            if notes:
                note = notes[0]
                lastname = note['lastname']
                firstname = note['firstname']
                note_id = note['id']
            else:
                return False

            cursor.bindValue(':date', now)
            cursor.bindValue(':note', trans['note'])
            cursor.bindValue(':category', trans['category'])
            cursor.bindValue(':product', trans['product'])
            cursor.bindValue(':price_name', trans['price_name'])
            cursor.bindValue(':quantity', trans['quantity'])
            cursor.bindValue(':price', trans['price'])
            cursor.bindValue(':firstname', firstname)
            cursor.bindValue(':lastname', lastname)
            cursor.bindValue(':liquid_quantity', trans.get('liquid_quantity', 0))
            cursor.bindValue(':percentage', trans.get('percentage', 0))
            cursor.bindValue(':deletable', trans.get('deletable', True))
            cursor.bindValue(':note_id', note_id)
            cursor.exec_()
            trans["id"] = cursor.lastInsertId()
            trans["date"] = now
            trans["note_id"] = note_id

        database.commit()
        asyncio.ensure_future(api.sde.send_history_lines(transactions))
        if not do_not:
            api.redis.send_message("enibar-notes", list(set(x['note'] for x in transactions)))
        return True


def rollback_transaction(id_, full=False):
    """ Rollback transaction
    And refill note with money

    :param int id_: Transaction id:
    :param bool full: Rollback the full transaction ?
    """
    trans = get_unique(id=id_)
    if not trans:
        return False

    try:
        def filter_(x):
            return x['firstname'] == trans['firstname'] and \
                x['lastname'] == trans['lastname']
        note = api.notes.get(filter_)[0]
    except IndexError:
        return False

    quantity = int(trans['quantity'])

    with Cursor() as cursor:
        if quantity > 1 and not full:
            cursor.prepare("UPDATE transactions SET quantity=quantity - 1,\
                    price=:price WHERE id=:id AND deletable=TRUE")
            price = trans['price'] / quantity
            cursor.bindValue(':price', trans['price'] - price)
            cursor.bindValue(':id', trans['id'])
            task = api.sde.send_history_lines([{
                "id": trans["id"],
                "price": trans["price"] - price,
                "quantity": quantity - 1}])
        else:
            task = api.sde.send_history_deletion([trans['id']])
            cursor.prepare("DELETE FROM transactions WHERE id=:id "
                           "AND deletable=TRUE")
            cursor.bindValue(':id', trans['id'])
            price = trans['price']

        cursor.exec_()
        if not cursor.lastError().isValid() and cursor.numRowsAffected() > 0:
            asyncio.ensure_future(task)
            api.redis.send_message("enibar-notes", [note['nickname']])
            return True
        task.close()
    return False


FILTER_FIELDS_CACHE = {}


def get_possible_filter_values(col, filters):
    """ Get all the possible values for a filter given all other applied filters

    :param str col: db column name
    :param dict filters: A dict giving corresponding value to filters
    """
    if not filters:
        sqlfilters = []
    else:
        sqlfilters = [c + "=:" + c for c in filters if c != col]

    if col == 'product' and filters.get('category', '') != "Note":
        sqlfilters.append("category != 'Note'")

    with Cursor() as cursor:
        cursor.prepare(
            """
            SELECT DISTINCT {c} FROM transactions
            {w} {filters}
            ORDER BY {c}
            """.format(c=col, w="WHERE" * bool(sqlfilters),
                       filters=' AND '.join(sqlfilters))
        )
        for key, value in filters.items():
            cursor.bindValue(":{}".format(key), value)

        cursor.exec_()

        if col not in FILTER_FIELDS_CACHE:
            FILTER_FIELDS_CACHE[col] = cursor.indexOf(col)

        while cursor.next():
            yield cursor.value(FILTER_FIELDS_CACHE[col])


TRANSACTS_FIELDS_CACHE = {}
TRANSACT_FIELDS = ['id', 'date', 'note', 'lastname', 'firstname', 'category',
                   'product', 'price_name', 'quantity', 'price', 'liquid_quantity', 'percentage']


def get(max_=None, reverse=False, **filter_):
    """ Get transactions matching filter.

    :param dict filter_: filter to apply
    """
    global TRANSACTS_FIELDS_CACHE
    cursor = api.base.filtered_getter("transactions", filter_, max_=max_, reverse=reverse)

    if TRANSACTS_FIELDS_CACHE == {}:
        TRANSACTS_FIELDS_CACHE = {field: cursor.indexOf(field) for field
                                  in TRANSACT_FIELDS}

    while cursor.next():
        yield {field: cursor.value(TRANSACTS_FIELDS_CACHE[field]) for field
               in TRANSACT_FIELDS}


get_unique = api.base.make_get_unique(get)
