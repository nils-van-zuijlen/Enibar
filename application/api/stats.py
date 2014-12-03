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
Stats
=====

This api provides some neat stats.
"""

from database import Cursor
import api.base
import settings


def get_red():
    """ Returns the sum of negative notes
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT SUM(note) AS total_red, COUNT(id) as nb_notes\
            FROM notes WHERE note < 0")
        cursor.exec_()
        cursor.next()
        return {'total_red': cursor.record().value('total_red'),
                'nb_notes': cursor.record().value('nb_notes'), }


def get_green():
    """ Returns the sum of positive notes
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT SUM(note) AS total_green, COUNT(id) as nb_notes\
            FROM notes WHERE note > 0")
        cursor.exec_()
        cursor.next()
        return {'total_green': cursor.record().value('total_green'),
                'nb_notes': cursor.record().value('nb_notes'), }


def get_sold_items():
    """ Returns stats on sold items excluding ecocups, refilling and emptying
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT COUNT(*) AS nb, product, category, price_name\
            FROM transactions GROUP BY category, product, price_name")
        cursor.exec_()
        while cursor.next():
            record = cursor.record()
            if record.value('product') not in ('', '-', settings.ECOCUP_NAME) and\
                    record.value('price_name') not in ('Solde', 'Rechargement'):
                yield {'product': record.value("product"),
                       'nb': record.value('nb'),
                       'category': record.value('category'),
                       'price_name': record.value('price_name'), }


def get_consumers():
    """ Return a list of consurmers with the amount bought.
    """
    with Cursor() as cursor:
        cursor.prepare("SELECT\
            SUM(CASE WHEN price > 0 THEN price ELSE 0 END) AS refilled,\
            SUM(CASE WHEN price < 0 THEN price ELSE 0 END) AS bought,\
            note FROM transactions GROUP BY note")
        cursor.exec_()
        while cursor.next():
            record = cursor.record()
            yield {'note': record.value('note'),
                   'bought': -record.value('bought'),
                   'refilled': record.value('refilled')}

