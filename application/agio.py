"""
Automatic AGIO

Must be frequently called by a cron job

"""

import settings

from PyQt5 import QtSql
from database import Cursor


if __name__ == "__main__":
    with Cursor() as cursor:
        cursor.prepare("""
            UPDATE notes SET note=(note + note * ? / 100), last_agio=CURDATE()
            WHERE hidden=0
            AND overdraft_date < DATE_SUB(CURDATE(), INTERVAL ? DAY)
            AND (last_agio < DATE_SUB(CURDATE(), INTERVAL ? DAY)
                 OR last_agio IS NULL)
            """
        )
        cursor.addBindValue(settings.AGIO_PERCENT)
        cursor.addBindValue(settings.AGIO_THRESHOLD)
        cursor.addBindValue(settings.AGIO_EVERY)
        cursor.exec_()

