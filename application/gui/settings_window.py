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

"""
SettingsWindow
====================


"""


from PyQt5 import QtWidgets, uic
import api.validator
import api.redis
import json
import settings


class SettingsWindow(QtWidgets.QDialog):
    """ RefillNote window class """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/settings_window.ui', self)

        self.on_change = api.validator.on_change(self, self.save_button)

        self.web_groupbox.on_change = self.on_change
        self.cotiz_groupbox.on_change = self.on_change
        self.ecocups_groupbox.on_change = self.on_change
        self.mails_groupbox.on_change = self.on_change
        self.agio_groupbox.on_change = self.on_change
        self.diverse_groupbox.on_change = self.on_change

        self.web_url_input.set_validator(api.validator.URL)
        self.web_url_input.setText(settings.WEB_URL)
        self.web_key_input.set_validator(api.validator.NAME)
        self.web_key_input.setText(settings.AUTH_SDE_TOKEN)
        self.web_proxy_url_input.set_validator(api.validator.NOTHING)
        self.web_proxy_url_input.setText(settings.PROXY_AUTH)
        self.web_proxy_url_input.setEnabled(False)

        if settings.USE_PROXY:
            self.web_use_proxy_input.setChecked(True)
            self.web_proxy_url_input.setEnabled(True)
        self.web_proxy_url_input.set_validator(api.validator.NAME)

        self.cotiz_noncotiz_input.set_validator(api.validator.NAME)
        self.cotiz_noncotiz_input.setText(settings.NONCOTIZ_CATEGORY)
        self.cotiz_price_input.set_validator(api.validator.NUMBER)
        self.cotiz_price_input.setText(str(settings.COTIZ_PRICE))

        self.ecocups_price_input.set_validator(api.validator.NUMBER)
        self.ecocups_price_input.setText(str(settings.ECOCUP_PRICE))
        self.ecocups_category_input.set_validator(api.validator.NAME)
        self.ecocups_category_input.setText(settings.ECOCUP_CATEGORY)
        self.ecocups_buy_input.set_validator(api.validator.NAME)
        self.ecocups_buy_input.setText(settings.ECOCUP_PRICE_TYPES['take'])
        self.ecocups_repay_input.set_validator(api.validator.NAME)
        self.ecocups_repay_input.setText(settings.ECOCUP_PRICE_TYPES['repay'])
        self.ecocups_name_input.set_validator(api.validator.NAME)
        self.ecocups_name_input.setText(settings.ECOCUP_NAME)

        self.smtp_server_address_input.set_validator(api.validator.NAME)
        self.smtp_server_address_input.setText(settings.SMTP_SERVER_ADDR)
        self.smtp_server_port_input.set_validator(api.validator.NUMBER)
        self.smtp_server_port_input.setText(str(settings.SMTP_SERVER_PORT))

        self.agio_threshold_input.set_validator(api.validator.NUMBER)
        self.agio_threshold_input.setText(str(settings.AGIO_THRESHOLD))
        self.agio_every_input.set_validator(api.validator.NUMBER)
        self.agio_every_input.setText(str(settings.AGIO_EVERY))
        self.agio_percent_input.set_validator(api.validator.NUMBER)
        self.agio_percent_input.setText(str(settings.AGIO_PERCENT))

        self.majoration_input.set_validator(api.validator.NUMBER)
        self.majoration_input.setText(str(settings.ALCOHOL_MAJORATION))

        self.show()

    def accept(self):
        """ Called when "Sauvegarder" is clicked
        """
        settings.WEB_URL = self.web_url_input.text()
        settings.AUTH_SDE_TOKEN = self.web_key_input.text()
        settings.USE_PROXY = int(self.web_use_proxy_input.isChecked())
        settings.PROXY_AUTH = self.web_proxy_url_input.text()

        settings.NONCOTIZ_CATEGORY = self.cotiz_noncotiz_input.text()
        settings.COTIZ_PRICE = float(self.cotiz_price_input.text())

        settings.ECOCUP_PRICE = float(self.ecocups_price_input.text())
        settings.ECOCUP_CATEGORY = self.ecocups_category_input.text()
        settings.ECOCUP_PRICE_TYPES = json.dumps({'take': self.ecocups_buy_input.text(), 'repay': self.ecocups_repay_input.text()})
        settings.ECOCUP_NAME = self.ecocups_name_input.text()

        settings.SMTP_SERVER_ADDR = self.smtp_server_address_input.text()
        settings.SMTP_SERVER_PORT = int(self.smtp_server_port_input.text())

        settings.AGIO_THRESHOLD = int(self.agio_threshold_input.text())
        settings.AGIO_EVERY = int(self.agio_every_input.text())
        settings.AGIO_PERCENT = float(self.agio_percent_input.text())

        settings.ALCOHOL_MAJORATION = float(self.majoration_input.text())

        api.redis.send_message("enibar-settings", "")
        super().accept()

    def on_proxy_usage_change(self, state):
        self.web_proxy_url_input.setEnabled(state)
        if state:
            self.web_proxy_url_input.set_validator(api.validator.NAME)
        else:
            self.web_proxy_url_input.set_validator(api.validator.NOTHING)
        self.on_change()
