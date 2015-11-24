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


def log_transaction(nickname, category, product, price_name, quantity, price,
        deletable=True):
    """ Insert a transaction log line in database

    :param str nickname: Note nickname
    :param str category: Product's category
    :param str product: Product's name
    :param str price_name: Product's price name
    :param int quantity: Product quantity on this transaction
    :param float price: total price of the transaction
    """
    with Cursor() as cursor:
        notes = api.notes.get(lambda x: x["nickname"] == nickname)
        if notes:
            lastname = notes[0]['lastname']
            firstname = notes[0]['firstname']
        else:
            lastname, firstname = "", ""

        cursor.prepare("""INSERT INTO transactions(date, note, category,
            product, price_name,quantity, price, firstname, lastname, deletable)
            VALUES(NOW(), :note, :category, :product, :price_name, :quantity,
            :price, :firstname, :lastname, :deletable)
            """
        )
        cursor.bindValue(':note', nickname)
        cursor.bindValue(':category', category)
        cursor.bindValue(':product', product)
        cursor.bindValue(':price_name', price_name)
        cursor.bindValue(':quantity', quantity)
        cursor.bindValue(':price', price)
        cursor.bindValue(':firstname', firstname)
        cursor.bindValue(':lastname', lastname)
        cursor.bindValue(':deletable', deletable)
        cursor.exec_()
        asyncio.ensure_future(api.sde.send_history_lines([{"id": cursor.lastInsertId(), "note": nickname, "category": category, "product": product, "price_name": price_name, "quantity": quantity, "price": price}]))
        return True


def log_transactions(transactions):
    """ Log multiple transactions

    :param list transactions:
    """
    with Database() as database:
        cache = {}
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("""INSERT INTO transactions(
                date, note, category, product, price_name,
                quantity, price, firstname, lastname, deletable
            )
            VALUES(
                NOW(), :note, :category, :product, :price_name,
                :quantity, :price, :firstname, :lastname, :deletable
            )""")
        for trans in transactions:
            # Fecth firstname and lastname of user with a bit of caching
            if not trans['note'] in cache:
                fetching_cursor = QtSql.QSqlQuery(database)
                fetching_cursor.prepare("""SELECT lastname, firstname
                    FROM notes WHERE nickname=:nick"""
                )
                fetching_cursor.bindValue(':nick', trans['note'])
                fetching_cursor.exec_()
                if fetching_cursor.next():
                    record = fetching_cursor.record()
                    lastname = record.value("lastname")
                    firstname = record.value("firstname")
                else:
                    # Nickname is a fake one, we must not fill lastname and
                    # firstname name
                    lastname, firstname = "", ""
                cache[trans['note']] = {
                    'lastname': lastname,
                    'firstname': firstname
                }
            else:
                lastname = cache[trans['note']]['lastname']
                firstname = cache[trans['note']]['firstname']

            cursor.bindValue(':note', trans['note'])
            cursor.bindValue(':category', trans['category'])
            cursor.bindValue(':product', trans['product'])
            cursor.bindValue(':price_name', trans['price_name'])
            cursor.bindValue(':quantity', trans['quantity'])
            cursor.bindValue(':price', trans['price'])
            cursor.bindValue(':firstname', firstname)
            cursor.bindValue(':lastname', lastname)
            cursor.bindValue(':deletable', trans.get('deletable', True))
            cursor.exec_()
            trans["id"] = cursor.lastInsertId()

        asyncio.ensure_future(api.sde.send_history_lines(transactions))
        database.commit()
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
                    price=:price WHERE id=:id AND deletable=1")
            price = trans['price'] / quantity
            cursor.bindValue(':price', trans['price'] - price)
            cursor.bindValue(':id', trans['id'])
            task = api.sde.send_history_lines([{"id": trans["id"], "price": trans["price"] - price, "quantity": quantity - 1}])
        else:
            task = api.sde.send_history_deletion([trans['id']])
            cursor.prepare("DELETE FROM transactions WHERE id=:id "
                "AND deletable=1")
            cursor.bindValue(':id', trans['id'])
            price = trans['price']

        cursor.exec_()
        if not cursor.lastError().isValid() and cursor.numRowsAffected() > 0:
            asyncio.ensure_future(task)
            return api.notes.transactions([note['nickname'], ], -price)
        else:
            return False


def get_grouped_entries(col, filters):
    """ Get grouped entries to list all distinct value for given column when
    row validate filters if any.

    :param str col: db column name
    :param dict filters: A dict giving carresponding value to columns
    """
    if not filters:
        sqlfilters = []
    else:
        sqlfilters = [c + "=:" + c for c in filters if c != col]

    with Cursor() as cursor:
        cursor.prepare("""
            SELECT {c} FROM transactions
            {w} {filters}
            GROUP BY binary {c}
            ORDER BY {c}
            """.format(c=col, w="WHERE" * bool(sqlfilters),
                filters=' AND '.join(sqlfilters))
        )
        for key, value in filters.items():
            cursor.bindValue(":{}".format(key), value)
        cursor.exec_()
        while cursor.next():
            yield cursor.record().value(col)


TRANSACTS_FIELDS_CACHE = {}
TRANSACT_FIELDS = ['id', 'date', 'note', 'lastname', 'firstname', 'category',
                   'product', 'price_name', 'quantity', 'price']


def get(max=None, reverse=False, **filter_):
    """ Get transactions matching filter.

    :param dict filter_: filter to apply
    """
    global TRANSACTS_FIELDS_CACHE
    cursor = api.base.filtered_getter("transactions", filter_, max=max, reverse=reverse)
    while cursor.next():
        record = cursor.record()
        if TRANSACTS_FIELDS_CACHE == {}:
            TRANSACTS_FIELDS_CACHE = {field: record.indexOf(field) for field
                                      in TRANSACT_FIELDS}
        yield {field: record.value(TRANSACTS_FIELDS_CACHE[field]) for field
               in TRANSACT_FIELDS}

get_unique = api.base.make_get_unique(get)
