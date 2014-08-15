"""
Prices API
==========


"""

from database import Cursor

def add_descriptor(name, category):
    """ Add price

    :param str name: Price name
    :param int category: category id
    :return int: Return price id created or None
    """
    with Cursor() as cursor:
        cursor.prepare("INSERT INTO price_description(label, category) \
            VALUES(:label, :category)")
        cursor.bindValue(":label", name)
        cursor.bindValue(":category", category)
        if cursor.exec_():
            return cursor.lastInsertId()
        else:
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




