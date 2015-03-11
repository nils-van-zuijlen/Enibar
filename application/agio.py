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
Automatic AGIO

Must be frequently called by a cron job

"""

import settings
import api.transactions

from PyQt5 import QtSql
from database import Database

if __name__ == "__main__":
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("""
            SELECT id, nickname, note FROM notes
            WHERE hidden=0
            AND overdraft_date < DATE_SUB(CURDATE(), INTERVAL ? DAY)
            AND (last_agio < DATE_SUB(CURDATE(), INTERVAL ? DAY)
                 OR last_agio IS NULL)
            """
        )
        cursor.addBindValue(settings.AGIO_THRESHOLD)
        cursor.addBindValue(settings.AGIO_EVERY)
        cursor.exec_()

        transactions = []
        while cursor.next():
            update = QtSql.QSqlQuery(database)
            update.prepare("""
                UPDATE notes
                SET note=note + note * ? / 100, last_agio=CURDATE()
                WHERE id=?
                """
            )
            update.addBindValue(settings.AGIO_PERCENT)
            update.addBindValue(cursor.record().value("id"))
            if update.exec_():
                balance = cursor.record().value("note")
                transactions.append({
                    'note': cursor.record().value("nickname"),
                    'category': 'AGIO',
                    'product': '',
                    'price_name': '',
                    'quantity': 1,
                    'price': balance * settings.AGIO_PERCENT / 100,
                })

        api.transactions.log_transactions(transactions)
        database.commit()

