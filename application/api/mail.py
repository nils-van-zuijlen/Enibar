import smtplib
import ssl
import sys
import re
from email.mime.text import MIMEText
from database import Cursor
import api.base

SMTP_SERVER_IP = 'smtp.enib.fr'
SMTP_SEVER_PORT = 25

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
#   "date_dernier_agio": "last_agio",
    "ecocups": "ecocups",
}


FILTER_UNITS = [
    24 * 3600,
    7 * 24 * 3600,
    30 * 24 * 3600,
]

def send_mail(to, subject, message, from_="cafeteria@enib.fr"):
    print("From:   ", from_)
    print("To:     ", to)
    print("Subject:", subject)
    print(message)
    return

    with smtplib.SMTP(SMTP_SERVER_IP, SMTP_SEVER_PORT) as server:
        message = MIMEText(message)
        message['subject'] = subject
        message['from'] = from_
        message['to'] = to
        message['bcc'] = bcc
        message['cc'] = cc
        server.send_message(message)

def format_message(message, note):
    for field in COMPLETION_FIELD:
        message = re.sub(
            "{" + field + "}", "{" + COMPLETION_FIELD[field] + "}", message
        )
    return message.format(**note)

def save_model(name, subject, message, filter_, filter_value):
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

def get_models(**filter_):
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

def get_scheduled_mails(**filter_):
    cursor = api.base.filtered_getter("scheduled_mails", filter_)
    while cursor.next():
        record = cursor.record()
        yield {
            'name': record.value('name'),
            'active': record.value('active'),
            'schedule_interval': record.value('schedule_interval'),
            'schedule_day': record.value('schedule_day'),
            'subject': record.value('subject'),
            'message': record.value('message'),
            'filter': record.value('filter'),
            'filter_value': record.value('filter_value'),
            'sender': record.value('sender'),
        }

def save_scheduled_mails(name, active, sched_int, sched_day, filter_,
        filter_val, subject, sender, message):
    with Cursor() as cursor:
        cursor.prepare("""
            INSERT INTO scheduled_mails(name, active, schedule_interval,
                schedule_day, filter, filter_value, subject, sender, message)
            VALUES(:name, :active, :sched_interval, :sched_day, :filter,
                :filter_val, :subject, :sender, :message)
            ON DUPLICATE KEY UPDATE name=:name, active=:active,
                schedule_interval=:sched_interval, schedule_day=:sched_day,
                filter=:filter, filter_value=:filter_val, subject=:subject,
                message=:message, sender=:sender
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

        cursor.exec_()
        return not cursor.lastError().isValid()


def delete_scheduled_mail(name):
    with Cursor() as cursor:
        cursor.prepare("DELETE FROM scheduled_mails WHERE name=:name")
        cursor.bindValue(':name', name)
        cursor.exec_()
        return not cursor.lastError().isValid()

def rename_scheduled_mail(name, newname):
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

def convert_interval(interval):
    for i, unit in reversed(list(enumerate(FILTER_UNITS))):
        if interval // unit == interval / unit:
            return (interval // unit, FILTER_UNITS.index(unit))

get_unique_model = api.base.make_get_unique(get_models)
get_unique_scheduled_mails = api.base.make_get_unique(get_scheduled_mails)

