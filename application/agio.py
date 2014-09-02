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
                SET note=ROUND(note + note * ? / 100, 2), last_agio=CURDATE()
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

