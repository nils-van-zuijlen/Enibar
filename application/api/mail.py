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

Mail API
========

Handle all mail related task.

"""

import sys
import smtplib
import ssl
import re
import datetime
from email.mime.text import MIMEText
from database import Cursor
import api.base
import api.notes
import settings


# Data used to convert french completion word to english database column name
# It's also used to propose a list of completion for mail message input.
COMPLETION_FIELD = {
    "id": "id",
    "surnom": "nickname",
    "nom": "lastname",
    "prenom": "firstname",
    "mail": "mail",
    "telephone": "tel",
    "date_naissance": "birthdate",
    "promo": "promo",
    "note": "note",
    "date_note_negative": "overdraft_date",
    "ecocups": "ecocups",
}


# Interval units used to match database schedule unit to Qt combobox indexes
INTERVAL_UNITS = [
    "day",
    "week",
    "month",
]

# Filters used too match notes we must send email to. Indexes are relevant and
# must match Qt combobox indexes.
FILTERS = [
    lambda x, y: True,
    lambda x, y: x['mail'] in y.split(','),
    lambda x, y: x['note'] >= float(y),
    lambda x, y: x['note'] < float(y),
]


def get_recipients(filter_, filter_arg):
    """ Get a list of all notes matching filter

    :param int filter_: Selected filter
    :param str filter_arg: Argument provided to filter
    :return list: Matching notes
    """
    try:
        filter_fnc = FILTERS[filter_]
        return api.notes.get(lambda x: filter_fnc(x, filter_arg) and x['mails_inscription'])
    except IndexError:
        return []
    except ValueError:
        return []


def send_mail(to, subject, message, from_="cafeteria@enib.fr"):
    """ Send mail

    :param str to: Mail recipient
    :param str subject: Mail subject
    :param str message: Mail message
    :param str from_: Mail sender
    """

    srv, port = settings.SMTP_SERVER_ADDR, settings.SMTP_SERVER_PORT
    with smtplib.SMTP(srv, port) as server:
        message = MIMEText(message, "html")
        message['subject'] = subject
        message['from'] = from_
        message['to'] = to
        try:
            server.send_message(message)
        except smtplib.SMTPRecipientsRefused:
            pass


def dummy_send_mail(to, subject, message, from_="cafeteria@enib.fr"):
    print("From:   ", from_)
    print("To:     ", to)
    print("Subject:", subject)
    print(message)


def format_message(message, note):
    """ Format massge
    Convert placeholders to their values.

    :param str message: input text to convert
    :param dict note: A dict describing a note
    :return str: text with converted placeholders to their values
    """
    note = dict(note)  # Create a copy of note to avoid modifying the real note
    for field in COMPLETION_FIELD:
        message = re.sub(
            "{" + field + "}", "{" + COMPLETION_FIELD[field] + "}", message
        )

    # Change all date to readable format
    note['birthdate'] = datetime.date.fromtimestamp(note['birthdate'])
    note['birthdate'] = note['birthdate'].strftime("%d/%m/%Y")
    if note['overdraft_date'].isValid():
        note['overdraft_date'] = note['overdraft_date'].toString("dd/MM/yyyy")
    else:
        note['overdraft_date'] = "Jamais"

    return message.format(**note)


def get_models(**filter_):
    """ Get model list

    :param kwargs **filters: Filter to apply when fetching models
    :return generator: Models
    """
    cursor = api.base.filtered_getter("mail_models", filter_)
    while cursor.next():
        record = cursor.record()
        yield {
            'name': record.value('name'),
            'subject': record.value('subject'),
            'message': record.value('message'),
            'filter': record.value('filter'),
            'filter_value': record.value('filter_value'),
        }


def save_model(name, subject, message, filter_, filter_value):
    """ Save mail model

    :param str name: Model name
    :param str subject: Model subject
    :param str message: Model message
    :param int filter_: Filter used to match notes when sending
    :param str filter_value: Filter additioal value
    :return bool: Operation succes or not
    """
    with Cursor() as cursor:
        cursor.prepare("""
            INSERT INTO mail_models(name, subject, message, filter, filter_value)
            VALUES (:name, :subject, :message, :filter, :filter_value)
            ON DUPLICATE KEY UPDATE subject=:subject, message=:message,
            filter=:filter, filter_value=:filter_value
            """
        )
        cursor.bindValue(':name', name)
        cursor.bindValue(':subject', subject)
        cursor.bindValue(':message', message)
        cursor.bindValue(':filter', filter_)
        cursor.bindValue(':filter_value', filter_value)
        cursor.exec_()
        return not cursor.lastError().isValid()


def delete_model(name):
    """ Delete model with given name

    :param str name: Model name
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM mail_models WHERE name=:name")
        cursor.bindValue(':name', name)
        cursor.exec_()
        return not cursor.lastError().isValid()


def get_scheduled_mails(**filter_):
    """ Get scheduled mails

    :param kwargs **filters: Filter to apply when fetching mails
    :return generator: scheduled mails
    """
    cursor = api.base.filtered_getter("scheduled_mails", filter_)
    while cursor.next():
        record = cursor.record()
        yield {
            'name': record.value('name'),
            'active': record.value('active'),
            'schedule_interval': record.value('schedule_interval'),
            'schedule_unit': record.value('schedule_unit'),
            'schedule_day': record.value('schedule_day'),
            'subject': record.value('subject'),
            'message': record.value('message'),
            'filter': record.value('filter'),
            'filter_value': record.value('filter_value'),
            'sender': record.value('sender'),
            'last_sent': record.value('last_sent'),
        }


def save_scheduled_mails(name, active, sched_int, sched_unit, sched_day,
        filter_, filter_val, subject, sender, message, last_sent):
    """ Save scheduled mail

    :param str name: Scheduled mail name
    :param bool active: Enable mail sending if True
    :param int sched_int: Schedule interval
    :param str sched_unit: One of the following: day, week, month
    :param int sched_day: Day the mail should be sent on
    :param int filter_: Filter used to match notes to send to
    ;parma str filter_val: Filter value
    :param str subject: Mail subject
    :param str sender: Mail sender
    :param str message: Mail content
    :param QDateTime last_sent: Last date message was sent
    :return bool: Operation success
    """
    with Cursor() as cursor:
        cursor.prepare("""
            INSERT INTO scheduled_mails(name, active, schedule_interval,
                schedule_day, filter, filter_value, subject, sender, message,
                schedule_unit, last_sent)
            VALUES(:name, :active, :sched_interval, :sched_day, :filter,
                :filter_val, :subject, :sender, :message, :schedule_unit,
                :last_sent)
            ON DUPLICATE KEY UPDATE name=:name, active=:active,
                schedule_interval=:sched_interval, schedule_day=:sched_day,
                filter=:filter, filter_value=:filter_val, subject=:subject,
                message=:message, sender=:sender, schedule_unit=:schedule_unit,
                last_sent=:last_sent
            """
        )

        cursor.bindValue(':name', name)
        cursor.bindValue(':active', active)
        cursor.bindValue(':sched_interval', sched_int)
        cursor.bindValue(':sched_day', sched_day)
        cursor.bindValue(':filter', filter_)
        cursor.bindValue(':filter_val', filter_val)
        cursor.bindValue(':subject', subject)
        cursor.bindValue(':sender', sender)
        cursor.bindValue(':message', message)
        cursor.bindValue(':schedule_unit', sched_unit)
        cursor.bindValue(':last_sent', last_sent)

        cursor.exec_()
        return not cursor.lastError().isValid()


def rename_scheduled_mail(name, newname):
    """ Rename scheduled mail

    :param str name: Mail name
    :param str newname: New mail name
    :return bool: Operation success
    """
    with Cursor() as cursor:
        cursor.prepare("""
            UPDATE scheduled_mails
            SET name=:newname
            WHERE name=:name
            """
        )
        cursor.bindValue(':name', name)
        cursor.bindValue(':newname', newname)
        cursor.exec_()
        return not cursor.lastError().isValid()


def delete_scheduled_mail(name):
    """ Delete scheduled mail

    :param str name: Name of the mail you want to delete
    :return bool: Operation success
    """
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM scheduled_mails WHERE name=:name")
        cursor.bindValue(':name', name)
        cursor.exec_()
        return not cursor.lastError().isValid()


get_unique_model = api.base.make_get_unique(get_models)
get_unique_scheduled_mails = api.base.make_get_unique(get_scheduled_mails)

