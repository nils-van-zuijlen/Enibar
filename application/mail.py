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
Send mails
==========

Script in charge to filter scheduled mails and send them when required.
It should be called by a cron job frequently enought to check mails at least
once a day.

"""

import api.mail
from PyQt5 import QtSql, QtCore
from database import Cursor

UNIT_TO_FUNC = {
    'day': lambda x, y: x.addDays(y),
    'week': lambda x, y: x.addDays(y * 7),
    'month': lambda x, y: x.addMonths(y)
}


def send_scheduled_mails():
    """ Send scheduled mails
    """
    with Cursor() as cursor:
        cursor.prepare("""
            SELECT * FROM scheduled_mails
            WHERE active is TRUE
            AND (schedule_day = DAYOFWEEK(NOW()) OR schedule_day = 0)
            """
        )

        cursor.exec_()
        now = QtCore.QDate.currentDate()
        while cursor.next():
            record = cursor.record()
            unit = record.value('schedule_unit')
            interval = record.value('schedule_interval')
            mail_data = {}

            # Exlude mail when it's too soon to send them
            if record.value('last_sent').isValid():
                if unit not in UNIT_TO_FUNC:
                    continue
                send_date = UNIT_TO_FUNC[unit](
                    record.value('last_sent'),
                    interval
                )
                if send_date > now:
                    continue

            # Ok send mail
            recipients = api.mail.get_recipients(
                record.value('filter'),
                record.value('filter_value'),
            )
            for recipient in recipients:
                if recipient['hidden'] or recipient['promo'] == "Prof":
                    continue
                subject = api.mail.format_message(
                    record.value('subject'),
                    recipient
                )
                message = api.mail.format_message(
                    record.value('message'),
                    recipient
                )
                api.mail.send_mail(
                    recipient['mail'],
                    subject,
                    message,
                    record.value('sender')
                )

            # Update database.
            with Cursor() as update_cursor:
                update_cursor.prepare("""
                    UPDATE scheduled_mails SET last_sent=CURDATE()
                    WHERE name=:name
                    """
                )
                update_cursor.bindValue(":name", record.value('name'))
                update_cursor.exec_()
                if update_cursor.lastError().isValid():
                    print(update_cursor.lastError().text())


if __name__ == "__main__":
    send_scheduled_mails()
