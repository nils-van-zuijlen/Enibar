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
    """ Log mulsiple transactions

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


def get(**filter_):
    """ Get transactions matching filter.

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("transactions", filter_)
    while cursor.next():
        yield {
            'id': cursor.record().value('id'),
            'date': cursor.record().value('date'),
            'note': cursor.record().value('note'),
            'category': cursor.record().value('category'),
            'product': cursor.record().value('product'),
            'price_name': cursor.record().value('price_name'),
            'quantity': cursor.record().value('quantity'),
            'price': cursor.record().value('price'),
        }

