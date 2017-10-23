# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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
Products
========

"""

from PyQt5 import QtSql
from database import Cursor, Database, SqlQuery
import api.categories
import api.base
import rapi

PRODUCT_FIELDS = ['id', 'name', 'category', 'percentage']


def add(name, *, category_name=None, category_id=None, percentage=0):
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
        cursor = SqlQuery(database)
        cursor.prepare("INSERT INTO products(name, category, percentage) VALUES(:name,\
                        :cat, :percentage)")
        cursor.bindValue(':name', name.strip())
        cursor.bindValue(':cat', cat[0]['id'])
        cursor.bindValue(':percentage', percentage)
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
                cursor.value('id')
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
    return rapi.products.remove(id_)


def rename(product_id, new_name):
    """ Rename a product
    """
    return rapi.products.rename(product_id, new_name)


def set_percentage(product_id, percentage):
    return rapi.products.set_percentage(product_id, percentage)


def get(**filter_):
    """ Get products filtered by given values
    Shuld be used like this api.products.get(name="machin", category=5)

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("products", filter_)
    while cursor.next():
        yield {field: cursor.value(field) for field in
               PRODUCT_FIELDS}


get_unique = api.base.make_get_unique(get)

