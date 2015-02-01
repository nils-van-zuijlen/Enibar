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
Prices
======


"""

from database import Cursor, Database
from PyQt5 import QtSql
import api.base
import settings


def add_descriptor(name, category):
    """ Add price descriptor

    :param str name: Price name
    :param int category: category id
    :return int: Return price id created or None
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("INSERT INTO price_description(label, category) \
            VALUES(:label, :category)")
        cursor.bindValue(":label", name)
        cursor.bindValue(":category", category)
        if cursor.exec_():
            desc_id = cursor.lastInsertId()
            cursor.prepare("SELECT id FROM products WHERE category=:category")
            cursor.bindValue(":category", category)
            if cursor.exec_():
                while cursor.next():
                    pcurser = QtSql.QSqlQuery(database)
                    pcurser.prepare("INSERT INTO prices(price_description, \
                            product, value) VALUES(:desc, :product, :value)")
                    pcurser.bindValue(":desc", desc_id)
                    pcurser.bindValue(":product", cursor.record().value('id'))
                    pcurser.bindValue(":value", 0.00)
                    pcurser.exec_()
            database.commit()
            return desc_id

        # Something went wrong
        database.rollback()
        return None


def remove_descriptor(descriptor_id):
    """ Remove price from category

    :param int descriptor_id: Price descriptor id
    :return bool: True if operation succeed
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM price_description WHERE id=:id")
        cursor.bindValue(":id", descriptor_id)
        return cursor.exec_()


def rename_descriptor(id_, name):
    """ Rename price descriptor

    :param int id_: Price descriptor id
    :return bool: True if operation succeed
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE price_description SET label=:label WHERE id=:id")
        cursor.bindValue(":id", id_)
        cursor.bindValue(":label", name)
        return cursor.exec_()


def get_descriptor(**kwargs):
    """ Get price descriptor

    :param \*\*kwargs: filters to apply
    """
    with Cursor() as cursor:
        request_filters = []
        for key in kwargs:
            request_filters.append("{key}=:{key}".format(key=key))
        request = "SELECT * FROM price_description WHERE {}".format(
            " AND ".join(request_filters)
        )
        cursor.prepare(request)
        for key, arg in kwargs.items():
            cursor.bindValue(":{}".format(key), arg)
        cursor.exec_()
        while cursor.next():
            record = cursor.record()
            yield {
                'id': record.value('id'),
                'label': record.value('label'),
                'category': record.value('category'),
            }


def add(product, price_description, value):
    """ Add price to product

    :param int product: Product id
    :param int price_description: Price description
    :param float value: Price
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO prices (product, price_description, value)\
        (SELECT :product, :price_description, :value FROM (SELECT 1) t WHERE\
        EXISTS(SELECT * FROM products INNER JOIN price_description ON\
        products.category=price_description.category WHERE products.id=:product\
        AND price_description.id=:price_description))")
        cursor.bindValue(':product', product)
        cursor.bindValue(':price_description', price_description)
        cursor.bindValue(':value', value)
        cursor.exec_()
        return cursor.lastInsertId()


def remove(price_id):
    """ Remove price

    :param int price_id: Price id
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM prices WHERE id=:id")
        cursor.bindValue(':id', price_id)
        return cursor.exec_()


def get(**kwargs):
    """ Get prices filtered by given values

    :param \*\*kwargs: filters to apply
    """
    with Cursor() as cursor:
        filters = []
        for key in kwargs:
            filters.append("prices.{key}=:{key}".format(key=key))
        cursor.prepare("SELECT prices.id as id,\
            prices.product as product,\
            prices.value as value,\
            price_description.label as label,\
            price_description.category as category, \
            categories.alcoholic AS alcoholic \
            from prices INNER JOIN price_description \
            INNER JOIN categories \
            ON prices.price_description=price_description.id \
            AND categories.id=price_description.category \
            {} {} ".format("WHERE" * bool(filters), " AND ".join(filters)))
        for key, arg in kwargs.items():
            cursor.bindValue(":{}".format(key), arg)

        if cursor.exec_():
            while cursor.next():
                record = cursor.record()
                yield {
                    'id': record.value('id'),
                    'label': record.value('label'),
                    'value': record.value('value') + settings.ALCOHOL_MAJORATION * record.value("alcoholic"),
                    'product': record.value('product'),
                    'category': record.value('category'),
                }


def set_barcode(id_, barcode):
    """ Change the barcod assiociated to a product
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO barcodes (price_id, value) VALUES(:price, :value)")
        cursor.bindValue(":price", id_)
        cursor.bindValue(":value", barcode)
        cursor.exec_()
        return not cursor.lastError().isValid()


def get_barcodes(price_id):
    """ Return a lit of barcodes assiociated with a price
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM barcodes WHERE price_id=:id")
        cursor.bindValue(":id", price_id)
        cursor.exec_()
        while cursor.next():
            record = cursor.record()
            yield {
                'id': record.value('id'),
                'price_id': record.value('price_id'),
                'value': record.value('value'),
            }


def delete_barcode(barcode):
    """ Delete a barcode
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM barcodes WHERE value=:barcode")
        cursor.bindValue(":barcode", barcode)
        return cursor.exec_()


def get_product_by_barcode(barcode):
    """ Returns a price id when provided a barcode
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM barcodes WHERE value=:barcode")
        cursor.bindValue(":barcode", barcode)
        cursor.exec_()
        if cursor.next():
            return cursor.record().value('price_id')
    return None


def set_value(id_, value):
    """ Set price value
    If you have to change value of multiple prices use set_multiple_values
    instead.

    :param int id_: price id
    :param float value: new price value
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE prices SET value=:value WHERE id=:id")
        cursor.bindValue(":id", id_)
        cursor.bindValue(":value", value)
        return cursor.exec_()


def set_multiple_values(prices):
    """ Update all prices with their new values
    Note: this function should be prefered when dealing with multiple prices at
    once for performance purposes.

    :param list prices: List of prices
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("UPDATE prices SET value=:value WHERE id=:id")
        for price in prices:
            cursor.bindValue(":id", price['id'])
            cursor.bindValue(":value", price['value'])
            cursor.exec_()

        database.commit()
        return True


get_unique = api.base.make_get_unique(get)
