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
Panels
======

"""

from PyQt5 import QtSql
from database import Cursor, Database
import api.base


def add(name):
    """ Add a panel.

    :param str name: The name of the tab.

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO panels(name) VALUES(:name)")
        cursor.bindValue(':name', name)
        if cursor.exec_():
            return cursor.lastInsertId()  # Return the created panel
        else:
            return None


def remove(name):
    """ Remove an panel

    :param str name: Panel name

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM panels WHERE name=:name")
        cursor.bindValue(':name', name)

        return cursor.exec_()


def add_product(paid, product):
    """ Add product

    :param int paid: Panel id
    :param int product: Product id
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO panel_content(panel_id, product_id) \
                VALUES(:paid, :poid)")
        cursor.bindValue(':paid', paid)
        cursor.bindValue(':poid', product)
        return cursor.exec_()


def hide(name):
    """ Hide a panel

    :param str name: The name of the panel

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE panels SET hidden=1 WHERE name=:name")
        cursor.bindValue(":name", name)
        return cursor.exec_()


def show(name):
    """ Show a panel

    :param str name: The name of the panel

    :return bool: True if success else False
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE panels SET hidden=0 WHERE name=:name")
        cursor.bindValue(":name", name)
        return cursor.exec_()


def add_products(paid, products):
    """ Add multpile product to panel content

    :param int paid: panel id
    :param list products: list of products id
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("INSERT INTO panel_content(panel_id, product_id) VALUES\
                (:paid, :poid)")
        for product in products:
            cursor.bindValue(":paid", paid)
            cursor.bindValue(":poid", product)
            cursor.exec_()
        database.commit()


def delete_product(paid, product):
    """ Delete product from panel

    :param int paid: Panel id
    :param int product: Product
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM panel_content WHERE panel_id=:panel_id and \
                product_id=:product_id")
        cursor.bindValue(':panel_id', paid)
        cursor.bindValue(':product_id', product)
        return cursor.exec_()


def delete_products(paid, products):
    """ Delete multiple products from panel

    :param int paid: Panel id
    :param int product: Product
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("DELETE FROM panel_content WHERE panel_id=:paid and \
                product_id=:poid")
        for product in products:
            cursor.bindValue(":paid", paid)
            cursor.bindValue(":poid", product)
            cursor.exec_()
        database.commit()


def get(**filter_):
    """ Get panel with given values

    :param dict filter_: filter to apply
    """
    cursor = api.base.filtered_getter("panels", filter_)
    while cursor.next():
        yield {
            'name': cursor.value('name'),
            'hidden': cursor.value('hidden'),
            'id': cursor.value('id'),
        }


def get_content(**kwargs):
    """ Get panel content

    :param kwargs: filter to apply
    """
    with Cursor() as cursor:
        filters = []
        for key in kwargs:
            filters.append("panel_content.{key}=:{key}".format(key=key))

        request = """SELECT panel_content.panel_id AS panel_id,
        products.id AS product_id,
        products.name AS product_name,
        products.percentage AS product_percentage,
        categories.id AS category_id,
        categories.name as category_name
        FROM panel_content
        JOIN products ON products.id=panel_content.product_id
        JOIN categories ON categories.id=products.category
        {} {}""".format("WHERE" * bool(len(filters)), " AND ".join(filters))

        cursor.prepare(request)
        for key, arg in kwargs.items():
            cursor.bindValue(":{}".format(key), arg)
        if cursor.exec_():
            while cursor.next():
                yield {
                    'panel_id': cursor.value('panel_id'),
                    'product_id': cursor.value('product_id'),
                    'product_name': cursor.value('product_name'),
                    'product_percentage': cursor.value('product_percentage'),
                    'category_id': cursor.value('category_id'),
                    'category_name': cursor.value('category_name'),
                }


get_unique = api.base.make_get_unique(get)

