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
Main file of the Application
"""
import asyncio
import aioredis
import api.redis
import api.sde
from database import Cursor, ping_sql
import json
import quamash
import sys
import gui.main_window
import settings
from PyQt5 import QtWidgets

SUB = None


async def install_redis_handle(app):
    global SUB
    SUB = await aioredis.create_redis((settings.HOST, 6379))
    res = await SUB.psubscribe("enibar-*")
    subscriber = res[0]

    while (await subscriber.wait_message()):
        reply = await subscriber.get_json()
        await app.redis_handle(reply[0].decode(), reply[1])


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
        TASKS.append(asyncio.ensure_future(api.sde.process_queue()))
        try:
            LOOP.run_until_complete(install_redis_handle(MYAPP))
        finally:
            for task in TASKS:
                task.cancel()
            LOOP.run_until_complete(SUB.punsubscribe("enibar-*"))
            LOOP.run_until_complete(SUB.quit())
            LOOP.run_until_complete(api.redis.connection.clear())

