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
        message = re.sub("{" + field + "}", "{" + COMPLETION_FIELD[field] + "}", message)
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

get_unique_model = api.base.make_get_unique(get_models)

if __name__ == "__main__":
    send_mail("a2levauf@enib.fr", to="a2levauf@enib.fr", subject="rembourse", message="ta note")

