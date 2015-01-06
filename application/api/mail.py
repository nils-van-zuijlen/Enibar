import smtplib
import ssl
import sys
import re
from email.mime.text import MIMEText

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


if __name__ == "__main__":
    send_mail("a2levauf@enib.fr", to="a2levauf@enib.fr", subject="rembourse", message="ta note")

