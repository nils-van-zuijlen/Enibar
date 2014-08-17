"""
Prices API
==========


"""

from database import Cursor, Database
from PyQt5 import QtSql

def add_descriptor(name, category):
    """ Add price

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
                    c = QtSql.QSqlQuery(database)
                    c.prepare("INSERT INTO prices(price_description, \
                            product, value) VALUES(:desc, :product, :value)")
                    c.bindValue(":desc", desc_id)
                    c.bindValue(":product", cursor.record().value('id'))
                    c.bindValue(":value", 0.00)
                    c.exec_()
            database.commit()
            return desc_id

        # Something went wrong
        database.rollback()
        return None


def remove_descriptor(id_):
    """ Remove price from category

    :param int id_: Price descriptor id_
    :return bool: True if operation succeed
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM price_description WHERE id=:id")
        cursor.bindValue(":id", id_)
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

def get_decriptor(**kwargs):
    """ Get price descriptor

    :param **kwargs: filters to apply
    """
    # TODO FIXME securiy issues
    with Cursor() as cursor:
        request_filters = []
        for key, arg in kwargs.items():
            request_filters.append("{}={}".format(key, arg))
        request = "SELECT * FROM price_description WHERE {}".format(
            " AND ".join(request_filters)
        )
        cursor.prepare(request)
        cursor.exec_()
        while cursor.next():
            yield {
                'id': cursor.record().value('id'),
                'label': cursor.record().value('label'),
                'category': cursor.record().value('category'),
            }


def add(product, price_description, value):
    """ Add price to product

    :param int product: Product id
    :param int price_description: Price description
    :param float value: Price
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO prices (product, price_description, value)\
                VALUES(:product, :price_description, :value)")
        cursor.bindValue(':product', product)
        cursor.bindValue(':price_description', price_description)
        cursor.bindValue(':value', value)
        if cursor.exec_():
            return cursor.lastInsertId()
        else:
            return None

def remove(id_):
    """ Remove price

    :param int id_: Price id
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM prices WHERE id=:id")
        cursor.bindValue(':id', id_)
        return cursor.exec_()

def get(**kwargs):
    """ Get prices filtered by given values

    :param **kwargs: filters to apply
    """
    with Cursor() as cursor:
        filters = []
        for key in kwargs:
            filters.append("{key}=:{key}".format(key=key))
        cursor.prepare("SELECT prices.id as id,\
            prices.product as product,\
            prices.value as value,\
            price_description.label as label,\
            price_description.category as category\
            from prices INNER JOIN price_description \
            ON prices.price_description=price_description.id \
            WHERE {} ".format(" AND ".join(filters))
        )
        for key, arg in kwargs.items():
            cursor.bindValue(":{}".format(key), arg)
        if cursor.exec_():
            while cursor.next():
                yield {
                    'id': cursor.record().value('id'),
                    'label': cursor.record().value('label'),
                    'value': cursor.record().value('value'),
                    'product': cursor.record().value('product'),
                    'category': cursor.record().value('category'),
                }


def get_unique(**kwargs):
    """ Get price with filter and return something only if unique

    :param **kwargs: filters
    """
    results = list(get(**kwargs))
    if len(results) != 1:
        return None
    else:
        return results[0]


def set_value(id_, value):
    """ Set price value

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
    error = False
    with Database() as db:
        db.transaction()
        cursor = QtSql.QSqlQuery(db)
        cursor.prepare("UPDATE prices SET value=:value WHERE id=:id")
        for price in prices:
            cursor.bindValue(":id", price['id'])
            cursor.bindValue(":value", price['value'])
            error = error or not cursor.exec_()

        if error:
            db.rollback()
            return False
        else:
            db.commit()
            return True

