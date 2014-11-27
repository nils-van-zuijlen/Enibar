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
Products management function
=================================

"""

from PyQt5 import QtSql
from database import Cursor, Database
import api.categories
import api.base

PRODUCT_FIELDS = ['name', 'category', 'barcode']


def add(name, *, category_name=None, category_id=None):
    """ Add a product.
    At least one of category_name and category_id arguments must not be None.
    If both are given then category_id is prefered.
    If any of the categoy prices wasn't created for this price then database
    transaction is rollback and so the product is not added.

    :param str name: Name.
    :param str category_name: Category name in which you want to add the product
    :param int category_id: Category id in which you want to add the produt \
    'alcool_pression'.

    :return bool: Operation status
    """
    if category_id:
        cat = list(api.categories.get(id=category_id))
    elif category_name:
        cat = list(api.categories.get(name=category_name))
    else:
        return None
    if not cat or len(cat) != 1:
        return None

    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("INSERT INTO products(name, category) VALUES(:name,\
                        :cat)")
        cursor.bindValue(':name', name.strip())
        cursor.bindValue(':cat', cat[0]['id'])
        if not cursor.exec_():
            database.rollback()
            return None

        product = cursor.lastInsertId()
        cursor.prepare("SELECT id FROM price_description WHERE category=:cat")
        cursor.bindValue(":cat", cat[0]['id'])
        cursor.exec_()

        while cursor.next():
            pcursor = QtSql.QSqlQuery(database)
            pcursor.prepare("INSERT INTO prices(product,\
                    price_description, value)\
                    VALUES(:product, :price_description, :value)")
            pcursor.bindValue(':product', product)
            pcursor.bindValue(
                ':price_description',
                cursor.record().value('id')
            )
            pcursor.bindValue(':value', '0.00')
            pcursor.exec_()
        database.commit()
        return product


def remove(id_):
    """ Remove a product

    :param str name: The name of the product to delete
    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM products WHERE id=:id")
        cursor.bindValue(':id', id_)
        return cursor.exec_()


def set_barcode(name, category, barcode):
    """ Set the barcode of a product in a category

        :param str name: The name of the product
        :param str category: The name of the category
        :return bool: True if success else False.
    """

    with Cursor() as cursor:
        cursor.prepare("UPDATE products SET barcode=:barcode WHERE name=:name\
                        AND category=:cat")

        category = api.categories.get_unique(name=category)
        cursor.bindValue(':barcode', barcode)
        cursor.bindValue(':name', name)
        cursor.bindValue(':cat', category['id'])

        return cursor.exec_()


def search_by_name(name):
    """ Search products by name

    :param str name: The name you want to search

    :return list: A list of product descriptions.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products WHERE name LIKE :name")

        cursor.bindValue(':name', "%{}%".format(name))
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   PRODUCT_FIELDS}


def get(**filter_):
    """ Get products filtered by given values
    Shuld be used like this api.products.get(name="machin", catgegory=5)

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("products", filter_)
    while cursor.next():
        yield {
            'id': cursor.record().value('id'),
            'name': cursor.record().value('name'),
            'category': cursor.record().value('category'),
            'barcode': cursor.record().value('barcode'),
        }


get_unique = api.base.make_get_unique(get)

