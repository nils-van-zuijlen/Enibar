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
import asyncio_redis
import api.redis
import json
import quamash
import sys
import gui.main_window
from PyQt5 import QtWidgets


@asyncio.coroutine
def install_redis_handle(app):
    connection = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)
    subscriber = yield from connection.start_subscribe()

    yield from subscriber.psubscribe(['enibar-*'])
    while True:
        reply = yield from subscriber.next_published()
        app.redis_handle(reply.channel, json.loads(reply.value))


if __name__ == "__main__":
    APP = QtWidgets.QApplication(sys.argv)
    LOOP = quamash.QEventLoop(APP)
    asyncio.set_event_loop(LOOP)
    MYAPP = gui.main_window.MainWindow()
    MYAPP.show()
    with LOOP:
        asyncio.async(install_redis_handle(MYAPP))
        asyncio.async(api.redis.connect())
        LOOP.run_forever()

