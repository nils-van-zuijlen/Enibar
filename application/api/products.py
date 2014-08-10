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

from database import Cursor


PRODUCT_FIELDS = ['name', 'category', 'price_unit', 'price_demi', 'price_pint',
                  'price_meter']


def add(name, category):
    """ Add a product.

    :param str name: Name.
    :param str category: Category. One of 'manger', 'soft', 'alcool_bouteille',
    'alcool_pression'.

    :return bool: Operation status
    """
    valid_category = (
        "manger",
        "soft",
        "alcool_bouteille",
        "alcool_pression"
    )
    if category not in valid_category:
        return False

    with Cursor() as cursor:
        cursor.prepare("INSERT INTO products (name, category) VALUES(:name,\
                        :category)")

        cursor.bindValue(':name', name)
        cursor.bindValue(':category', category)

        return cursor.exec_()


def remove(name):
    """ Remove a product

    :param str name: The name of the product to delete

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM products WHERE name=:name")

        cursor.bindValue(':name', name)

        return cursor.exec_()


def get_all():
    """ List all products

    :return dict: All products
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products")
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   PRODUCT_FIELDS}


def set_prices(name, unit=None, demi=None, pint=None, meter=None):
    """ Set prices for a product

    :param float unit: Price for an unit.
    :param float demi: Price of a « demi ».
    :param float pint: Price of a pint.
    :param float meter: Price of a meter.

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE products SET price_unit=:unit, price_demi=:demi,\
                        price_pint=:pint, price_meter=:meter WHERE name=:name")

        cursor.bindValue(':unit', unit)
        cursor.bindValue(':demi', demi)
        cursor.bindValue(':pint', pint)
        cursor.bindValue(':meter', meter)
        cursor.bindValue(':name', name)

        return cursor.exec_()

def set_category(name, category):
    """ Set product category

    :param str name: Name of the product
    :param str category: category of the product

    :return bool: Operation status
    """

def get_by_category(category):
    """ Get products by category

    :param str category: The category the products are in.

    :return list: A list of product descriptions.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products WHERE category=:category")

        cursor.bindValue(':category', category)
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in
                   PRODUCT_FIELDS}


def get_by_name(name):
    """ Get products by name

    :param str name: name of the product.

    :return list: A list of product descriptions.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products WHERE name LIKE :name")

        cursor.bindValue(':name', "%{}%".format(name))
        cursor.exec_()

        if cursor.next():
            return {field: cursor.record().value(field) for field in
                    PRODUCT_FIELDS}


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

