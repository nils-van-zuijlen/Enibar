# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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
Main file of the Application
"""
import asyncio
import aioredis
import api.redis
import api.sde
from database import ping_sql
import datetime
import quamash
import sys
import gui.main_window
import gui.utils
import settings
from PyQt5 import QtWidgets
import random


def excepthook(*args):
    sys.__excepthook__(*args)
    sys.exit(1)


sys.excepthook = excepthook
SUB = None

VERSION = 3
try:
    CURRENT_VERSION = int(api.redis.get_key_blocking("ENIBAR_VERSION").decode())
except ValueError:
    CURRENT_VERSION = VERSION

if VERSION < CURRENT_VERSION:
    APP = QtWidgets.QApplication(sys.argv)
    gui.utils.error("Update", "Please update")
    sys.exit(1)
elif VERSION > CURRENT_VERSION:
    api.redis.set_key_blocking("ENIBAR_VERSION", VERSION)


class Tee(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        self.data = ""

    def write(self, data):
        self.data += data
        if '\n' in self.data:
            data, self.data = self.data.split('\n', 1)
            d = datetime.datetime.now()
            fdata = "{}: {}\n".format(d.isoformat(' '), data)
            self.file.write(fdata)
            data = "\033[31m{}\033[0m: {}\n".format(d.isoformat(' '), data)
            self.stdout.write(data)
            self.stdout.flush()

    def flush(self):
        self.stdout.flush()


t = Tee("error", "a")

async def joke(app):
    color = ['red', 'blue']
    i = 0
    while True:
        app.setStyleSheet("background-color: hsl({}, 255, 255);".format(i))
        app.note_history.setStyleSheet("background-color: hsl({}, 255, 255);".format(i))
        await asyncio.sleep(0.05)
        i = (i + 1) % 360


async def install_redis_handle(app):
    global SUB
    while True:
        SUB = await aioredis.create_redis((settings.REDIS_HOST, 6379), password=settings.REDIS_PASSWORD)
        res = await SUB.psubscribe("enibar-*")
        subscriber = res[0]

        while await subscriber.wait_message():
            reply = await subscriber.get_json()
            await app.redis_handle(reply[0].decode(), reply[1])
        await asyncio.sleep(1)


if __name__ == "__main__":
    APP = QtWidgets.QApplication(sys.argv)
    LOOP = quamash.QEventLoop(APP)
    TASKS = []
    asyncio.set_event_loop(LOOP)

    with LOOP:
        LOOP.run_until_complete(api.redis.connect())
        MYAPP = gui.main_window.MainWindow()
        MYAPP.show()
        TASKS.append(asyncio.ensure_future(ping_sql(MYAPP)))
        TASKS.append(asyncio.ensure_future(api.redis.ping_redis()))
        TASKS.append(asyncio.ensure_future(api.sde.process_queue()))
        TASKS.append(asyncio.ensure_future(install_redis_handle(MYAPP)))
        TASKS.append(asyncio.ensure_future(joke(MYAPP)))
        try:
            LOOP.run_forever()
        finally:
            for task in TASKS:
                task.cancel()
            LOOP.run_until_complete(SUB.punsubscribe("enibar-*"))
            LOOP.run_until_complete(SUB.quit())
            api.redis.connection.close()
            LOOP.run_until_complete(api.redis.connection.wait_closed())


