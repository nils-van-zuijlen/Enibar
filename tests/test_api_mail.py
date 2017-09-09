
# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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

import basetest
import freezegun
import time
import os
import os.path
import PyQt5
import api.mail
import api.notes
import api.redis
import mock


class MailTest(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        if os.path.isfile("mail.log"):
            os.remove("mail.log")
        text = "cocou"
        api.notes.add(text, text, text, text, text,
            "24/12/2014", '1A', "", True, False)
        for i in range(10):
            text = "note{}".format(i)
            api.notes.add(text, text, text, text, text,
                "24/12/2014", '1A', "", True, True)
            if i < 5:
                diff = -5
            elif i == 5:
                diff = 0
            elif i > 5:
                diff = 5
            api.notes.transactions(api.notes.get(lambda x: x['nickname'] == text), diff)

    def _populate_models(self, count=10):
        """ Populate database with model

        :param int count: Number of model to generate
        :return list: model list
        """
        models = []
        for i in range(count):
            models.append({
                'name': "model name {}".format(i),
                'subject': "model subject {}".format(i),
                'message': "message " + "content " * i,
                'filter': i % len(api.mail.FILTERS),
                'filter_value': "test filter_storage" * (i % len(api.mail.FILTERS)),
            })
            api.mail.save_model(
                models[i]['name'],
                models[i]['subject'],
                models[i]['message'],
                models[i]['filter'],
                models[i]['filter_value']
            )
        return models

    def _populate_scheduled_mails(self, count=10):
        """ Populate database with scheduled mail

        :param int count: Number of mail to generate
        :param list: mail list
        """
        mails = []
        for i in range(count):
            mails.append({
                'name': "mail name {}".format(i),
                'active': 1,
                'schedule_interval': 1,
                'schedule_unit': "day",
                'schedule_day': 0,
                'subject': "mail subject {}".format(i),
                'message': "mail message {}".format(i),
                'filter': 0,
                'filter_value': "",
                'sender': "sender@enib.fr",
                'last_sent': PyQt5.QtCore.QDate(),
            })
            api.mail.save_scheduled_mails(
                mails[i]['name'],
                mails[i]['active'],
                mails[i]['schedule_interval'],
                mails[i]['schedule_unit'],
                mails[i]['schedule_day'],
                mails[i]['filter'],
                mails[i]['filter_value'],
                mails[i]['subject'],
                mails[i]['sender'],
                mails[i]['message'],
                mails[i]['last_sent']
            )
        return mails

    def test_get_recipients(self):
        """ Testing get recipients
        """
        self.assertEqual(api.notes.get(lambda x: x['mails_inscription']), api.mail.get_recipients(0, ""))
        self.assertEqual(api.notes.get(lambda x: x['mail'] in ('note1', 'note2')), api.mail.get_recipients(1, "note1,note2"))
        self.assertEqual(api.notes.get(lambda x: x['note'] >= 0 and x['mails_inscription']), api.mail.get_recipients(2, "0"))
        self.assertEqual(api.notes.get(lambda x: x['note'] < 0 and x['mails_inscription']), api.mail.get_recipients(3, "0"))
        self.assertEqual([], api.mail.get_recipients(2, ""))
        self.assertEqual([], api.mail.get_recipients(520, ""))

    def test_format_message(self):
        """ Testing mail message format
        """

        note = {
            'nickname': "Nickname",
            'lastname': "Lastname",
            'firstname': "Firstname",
            'mail': "m2blabla@enib.fr",
            'tel': "+33605040302",
            'birthdate': 1419397200,
            'promo': '1A',
            'overdraft_date': PyQt5.QtCore.QDate(2014, 5, 1),
            'note': -25,
            'id': 2,
            'ecocups': 5
        }
        message = api.mail.format_message(
            "{id} {surnom} {nom} {prenom} {mail} {telephone} {date_naissance} "
            "{promo} {note} {date_note_negative} {ecocups}", note
        )
        self.assertEqual(message, "2 Nickname Lastname Firstname "
                "m2blabla@enib.fr +33605040302 " + "24/12/2014" + " 1A -25 01/05/2014 5"
        )

        note = {
            'nickname': "Nickname",
            'lastname': "Lastname",
            'firstname': "Firstname",
            'mail': "m2blabla@enib.fr",
            'tel': "+33605040302",
            'birthdate': 1419397200,
            'promo': '1A',
            'overdraft_date': PyQt5.QtCore.QDate(),
            'note': -25,
            'id': 2,
            'ecocups': 5
        }
        message = api.mail.format_message(
            "{id} {surnom} {nom} {prenom} {mail} {telephone} {date_naissance} "
            "{promo} {note} {date_note_negative} {ecocups}", note
        )
        self.assertEqual(message, "2 Nickname Lastname Firstname "
                "m2blabla@enib.fr +33605040302 " + "24/12/2014" + " 1A -25 Jamais 5"
        )

    def test_get_models(self):
        """ Testing get mail models
        """
        models = self._populate_models()
        self.assertEqual(models, list(api.mail.get_models()))
        self.assertEqual({'name': "model name 0", 'subject': "model subject 0",
            'message': "message ", 'filter': 0, 'filter_value': ""},
            api.mail.get_unique_model(name="model name 0")
        )

    def test_save_model(self):
        """ Testing save mail model
        """
        models = []
        for i in range(10):
            models.append({
                'name': "model name {}".format(i),
                'subject': "model subject {}".format(i),
                'message': "message " + "content " * i,
                'filter': i % len(api.mail.FILTERS),
                'filter_value': "test filter_storage" * (i % len(api.mail.FILTERS)),
            })
            self.assertTrue(api.mail.save_model(
                models[i]['name'],
                models[i]['subject'],
                models[i]['message'],
                models[i]['filter'],
                models[i]['filter_value']
            ))
        self.assertEqual(models, list(api.mail.get_models()))
        self.assertFalse(api.mail.save_model(
            "Wrong",
            "Wrong",
            "{hehe}",
            1,
            "test"
        ))

    def test_delete_model(self):
        """ Testing mail model deletion
        """
        models = self._populate_models()
        self.assertTrue(api.mail.delete_model("model name 0"))
        models = models[1:]
        self.assertEqual(models, list(api.mail.get_models()))

    def test_get_scheduled_mails(self):
        """ Testing get scheduled mail
        """
        mails = self._populate_scheduled_mails()
        self.assertEqual(mails, list(api.mail.get_scheduled_mails()))
        self.assertEqual(mails[0], api.mail.get_unique_scheduled_mails(name="mail name 0"))
        self.assertEqual([], list(api.mail.get_scheduled_mails(name="qsdqslkjdlqkj")))

    def test_save_scheduled_mails(self):
        """ Testing save scheduled mails
        """
        mails = []
        mails.append({
            'name': "mail name 0",
            'active': 1,
            'schedule_interval': 1,
            'schedule_unit': "day",
            'schedule_day': 0,
            'subject': "mail subject 0",
            'message': "mail message 0",
            'filter': 0,
            'filter_value': "",
            'sender': "sender@enib.fr",
            'last_sent': PyQt5.QtCore.QDate(),
        })
        self.assertTrue(api.mail.save_scheduled_mails(
            mails[0]['name'],
            mails[0]['active'],
            mails[0]['schedule_interval'],
            mails[0]['schedule_unit'],
            mails[0]['schedule_day'],
            mails[0]['filter'],
            mails[0]['filter_value'],
            mails[0]['subject'],
            mails[0]['sender'],
            mails[0]['message'],
            mails[0]['last_sent']
        ))
        self.assertEqual(mails, list(api.mail.get_scheduled_mails()))

        mails[0]["active"] = 0
        self.assertTrue(api.mail.save_scheduled_mails(
            mails[0]['name'],
            mails[0]['active'],
            mails[0]['schedule_interval'],
            mails[0]['schedule_unit'],
            mails[0]['schedule_day'],
            mails[0]['filter'],
            mails[0]['filter_value'],
            mails[0]['subject'],
            mails[0]['sender'],
            mails[0]['message'],
            mails[0]['last_sent']
        ))
        self.assertEqual(mails, list(api.mail.get_scheduled_mails()))

        mails.append({
            'name': "mail name 1",
            'active': 1,
            'schedule_interval': 1,
            'schedule_unit': "day",
            'schedule_day': 0,
            'subject': "mail subject 1",
            'message': "mail message 1",
            'filter': 0,
            'filter_value': "",
            'sender': "sender@enib.fr",
            'last_sent': PyQt5.QtCore.QDate(),
        })
        self.assertTrue(api.mail.save_scheduled_mails(
            mails[1]['name'],
            mails[1]['active'],
            mails[1]['schedule_interval'],
            mails[1]['schedule_unit'],
            mails[1]['schedule_day'],
            mails[1]['filter'],
            mails[1]['filter_value'],
            mails[1]['subject'],
            mails[1]['sender'],
            mails[1]['message'],
            mails[1]['last_sent']
        ))
        self.assertEqual(mails, list(api.mail.get_scheduled_mails()))
        self.assertFalse(api.mail.save_scheduled_mails(
            "Wrong",
            1,
            1,
            "day",
            0,
            0,
            "",
            "Wrong",
            "sender@enib.fr",
            "{Wrong}",
            PyQt5.QtCore.QDate()
        ))

    def test_rename_scheduled_mail(self):
        """ Testing rename shceuled mail
        """
        mails = self._populate_scheduled_mails()
        mails[0]['name'] = "Renamed!"
        mails.append(mails[0])
        del mails[0]
        self.assertTrue(api.mail.rename_scheduled_mail("mail name 0", "Renamed!"))
        self.assertEqual(mails, list(api.mail.get_scheduled_mails()))

    def test_delete_scheduled_mail(self):
        """ Testing delete scheduled mail
        """
        mails = self._populate_scheduled_mails()
        self.assertTrue(api.mail.delete_scheduled_mail(mails[0]['name']))
        self.assertEqual(mails[1:], list(api.mail.get_scheduled_mails()))

    @freezegun.freeze_time("1994-02-01 00:00:00")
    def test_success_mail_logging(self):
        """ Testing successfully sent mail logging
        """
        return
        api.mail.log_mail("a2levauf@enib.fr", "Test", "Test", "cafeteria@enib.fr")
        with open("mail.log") as logfile:
            self.assertEqual(logfile.read(),
                "Mail sent on 1994-02-01 00:00:00 from cafeteria@enib.fr to a2levauf@enib.fr\n"
                "Subject : Test\n"
                "Message :\n"
                "\n"
                "Test\n"
                "\n"
                "\n"
                "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            )

    @freezegun.freeze_time("1994-02-01 00:00:00")
    def test_fail_mail_logging(self):
        """ Testing fail sent mail logging
        """
        api.mail.log_mail("a2levauf@enib.fr", "Test", "Test", "cafeteria@enib.fr", Exception)
        with open("mail.log") as logfile:
            self.assertEqual(logfile.read(),
                "Mail not sent on 1994-02-01 00:00:00 from cafeteria@enib.fr to a2levauf@enib.fr with error <class 'Exception'>\n"
                "Subject : Test\n"
                "Message :\n"
                "\n"
                "Test\n"
                "\n"
                "\n"
                "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            )

    @mock.patch('smtplib.SMTP')
    @mock.patch('random.randrange')  # Fix the boundary
    @mock.patch('os.urandom')  # Fix the Message-ID
    @freezegun.freeze_time("1994-02-01 00:00:00")
    def test_send_mail(self, urandom, randrange, smtp):
        """ Testing sending a mail
        """
        randrange.return_value = 0
        urandom.return_value = b"01234567"
        self.assertTrue(api.mail.send_mail("eijebong@bananium.fr", "test", "test"))

        smtp.return_value.__enter__.return_value.sendmail.assert_called_with("cafeteria@enib.fr", "eijebong@bananium.fr", 'Content-Type: multipart/alternative; boundary="===============0000000000000000000=="\nMIME-Version: 1.0\nsubject: test\nTo: eijebong@bananium.fr\nFrom: cafeteria@enib.fr\nDate: Tue, 01 Feb 1994 00:00:00 \nMessage-ID: <GAYTEMZUGU3DO.GAYTEMZUGU3DO@enibar.enib.net>\n\n--===============0000000000000000000==\nContent-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\ntest\n--===============0000000000000000000==\nContent-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n<!dotcype html>\n<html><body>test</body></html>\n--===============0000000000000000000==--\n')

    @mock.patch('smtplib.SMTP')
    @freezegun.freeze_time("1994-02-01 00:00:00")
    def test_send_mail_fail(self, smtp):
        smtp.return_value.__enter__.return_value.sendmail.side_effect = Exception("Error")
        self.assertFalse(api.mail.send_mail("eijebong@bananium.fr", "test", "test"))
        with open("mail.log") as logfile:
            self.assertEqual(logfile.read(),
                "Mail not sent on 1994-02-01 00:00:00 from cafeteria@enib.fr to eijebong@bananium.fr with error Error\n"
                "Subject : test\n"
                "Message :\n"
                "\n"
                "<!dotcype html>\n"
                "<html><body>test</body></html>\n"
                "\n"
                "\n"
                "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            )

