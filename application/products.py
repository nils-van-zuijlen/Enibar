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


FIELDS = ['name', 'category', 'price_unit', 'price_demi', 'price_pint',
          'price_meter']


def add(name, category):
    """ Add a product.

    :param str name: Name.
    :param str category: Category. One of 'manger', 'soft', 'alcool'.

    :return int: The id of the product added if success else -1.
    """
    if category not in ("manger", "soft", "alcool"):
        return -1

    with Cursor() as cursor:
        cursor.prepare("INSERT INTO products (name, category) VALUES(:name,\
                        :category)")

        cursor.bindValue(':name', name)
        cursor.bindValue(':category', category)

        if cursor.exec_():
            return cursor.lastInsertId()

        return -1


def remove(id_):
    """ Remove a product

    :param int id_: The id of the product to delete

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM products WHERE id=:id")

        cursor.bindValue(':id', id_)

        return cursor.exec_()


def set_prices(id_, unit=None, demi=None, pint=None, meter=None):
    """ Set prices for a product

    :param float unit: Price for an unit.
    :param float demi: Price of a « demi ».
    :param float pint: Price of a pint.
    :param float meter: Price of a meter.

    :return bool: True if success else False.
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE products SET price_unit=:unit, price_demi=:demi,\
                        price_pint=:pint, price_meter=:meter WHERE id=:id")

        cursor.bindValue(':unit', unit)
        cursor.bindValue(':demi', demi)
        cursor.bindValue(':pint', pint)
        cursor.bindValue(':meter', meter)
        cursor.bindValue(':id', id_)

        return cursor.exec_()


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
            yield {field: cursor.record().value(field) for field in FIELDS}


def get_by_name(name):
    """ Get products by name

    :param str name: The name you want to search

    :return list: A list of product descriptions.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products WHERE name LIKE :name")

        cursor.bindValue(':name', "%{}%".format(name))
        cursor.exec_()

        while cursor.next():
            yield {field: cursor.record().value(field) for field in FIELDS}


def get_by_id(id_):
    """ Get product by id

    :param int id_: The id of the product.

    :return dict: Description of the product or None if not found.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM products WHERE id=:id")

        cursor.bindValue(":id", id_)

        cursor.exec_()
        if cursor.next():
            return {field: cursor.record().value(field) for field in FIELDS}
        else:
            return None

