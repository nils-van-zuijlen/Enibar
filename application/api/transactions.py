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
Transaction API

Provide usefull api to interact with transaction hisotry and log, every
consumption bought.
"""

from PyQt5 import QtSql
from database import Database, Cursor
import api.base
import api.notes


def log_transaction(nickname, category, product, price_name, quantity, price):
    """ Insert a transaction log line in database

    :param str nickname: Note nickname
    :param str category: Product's category
    :param str product: Product's name
    :param str price_name: Product's price name
    :param int quantity: Product quantity on this transaction
    :param float price: total price of the transaction
    """
    # pylint: disable=too-many-arguments
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO transactions(date, note, category, product,\
                price_name, quantity, price) VALUES(NOW(), :note, :category, \
                :product, :price_name, :quantity, :price)")
        cursor.bindValue(':note', nickname)
        cursor.bindValue(':category', category)
        cursor.bindValue(':product', product)
        cursor.bindValue(':price_name', price_name)
        cursor.bindValue(':quantity', quantity)
        cursor.bindValue(':price', price)
        return cursor.exec_()


def log_transactions(transactions):
    """ Log multiple transactions

    :param list transactions:
    """
    with Database() as database:
        error = False
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("INSERT INTO transactions(date, note, category, product,\
                price_name, quantity, price) VALUES(NOW(), :note, :category, \
                :product, :price_name, :quantity, :price)")
        for trans in transactions:
            cursor.bindValue(':note', trans['note'])
            cursor.bindValue(':category', trans['category'])
            cursor.bindValue(':product', trans['product'])
            cursor.bindValue(':price_name', trans['price_name'])
            cursor.bindValue(':quantity', trans['quantity'])
            cursor.bindValue(':price', trans['price'])
            error = error or not cursor.exec_()

    if not error:
        database.commit()
        return True
    else:
        database.rollback()
        return False


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
        note = list(api.notes.get(lambda x: x['nickname'] == trans['note']))[0]
    except IndexError:
        return False

    try:
        quantity = int(trans['quantity'])
    except ValueError:
        quantity = 1

    with Cursor() as cursor:
        if quantity > 1 and not full:
            cursor.prepare("UPDATE transactions SET quantity=quantity - 1,\
                    price=? WHERE id=?")
            price = round(trans['price'] / quantity, 2)
            cursor.addBindValue(trans['price'] - price)
            cursor.addBindValue(trans['id'])
        else:
            cursor.prepare("DELETE FROM transactions WHERE id=?")
            cursor.addBindValue(trans['id'])
            price = trans['price']

        if cursor.exec_():
            return api.notes.transaction(note['nickname'], -price)
        else:
            return False

TRANSACTS_FIELDS_CACHE = {}
TRANSACT_FIELDS = ['id', 'date', 'note', 'category', 'product', 'price_name',
                   'quantity', 'price']


def get(**filter_):
    """ Get transactions matching filter.

    :param dict filter_: filter to apply
    """
    # pylint: disable=global-statement
    global TRANSACTS_FIELDS_CACHE
    cursor = api.base.filtered_getter("transactions", filter_)
    while cursor.next():
        record = cursor.record()
        if TRANSACTS_FIELDS_CACHE == {}:
            TRANSACTS_FIELDS_CACHE = {field: record.indexOf(field) for field
                                      in TRANSACT_FIELDS}
        yield {field: record.value(TRANSACTS_FIELDS_CACHE[field]) for field
               in TRANSACT_FIELDS}


def get_reversed(**filter_):
    """ Get transactions matching filter. Reversed.

    :param dict filter_: filter to apply
    """
    # pylint: disable=global-statement
    global TRANSACTS_FIELDS_CACHE
    cursor = api.base.filtered_getter("transactions", filter_)
    cursor.last()
    record = cursor.record()
    if TRANSACTS_FIELDS_CACHE == {}:
        TRANSACTS_FIELDS_CACHE = {field: record.indexOf(field) for field
                                  in TRANSACT_FIELDS}
    yield {field: record.value(TRANSACTS_FIELDS_CACHE[field]) for field
           in TRANSACT_FIELDS}
    while cursor.previous():
        record = cursor.record()
        yield {field: record.value(TRANSACTS_FIELDS_CACHE[field]) for field
               in TRANSACT_FIELDS}

# pylint: disable=invalid-name
get_unique = api.base.make_get_unique(get)

