# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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
Automatic AGIO

Must be frequently called by a cron job

"""

import asyncio
import settings
import api.transactions
import api.redis

from PyQt5 import QtSql
from database import Database


if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(api.redis.connect())

    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("""
        SELECT id, nickname, note FROM notes WHERE
            NOT EXISTS(
                SELECT note, category FROM note_categories_assoc JOIN note_categories
                ON note_categories.hidden=TRUE AND note_categories.id=category
                WHERE note=notes.id
            )
            AND overdraft_date < (DATE(NOW()) - INTERVAL '%s DAYS')
            AND agios_inscription=TRUE
            AND (last_agio < (DATE(NOW()) - INTERVAL '%s DAYS') OR last_agio IS NULL)
            """ % (settings.AGIO_THRESHOLD, settings.AGIO_EVERY)
        )
        cursor.exec_()

        transactions = []
        while cursor.next():
            update = QtSql.QSqlQuery(database)
            update.prepare("""
                UPDATE notes
                SET last_agio=DATE(NOW())
                WHERE id=?
                """)

            update.addBindValue(cursor.value("id"))
            if update.exec_():
                balance = cursor.value("note")
                transactions.append({
                    'note': cursor.value("nickname"),
                    'category': 'AGIO',
                    'product': '',
                    'price_name': '',
                    'quantity': 1,
                    'price': balance * settings.AGIO_PERCENT / 100,
                })

        api.transactions.log_transactions(transactions)
        database.commit()

    async def wait_5s():
        await asyncio.sleep(5)

    LOOP.run_until_complete(wait_5s())
