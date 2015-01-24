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
import quamash
import sys
import gui.main_window
from PyQt5 import QtWidgets


def update(app, loop):
    t = loop.create_task(app.notes_list.on_timer())
    loop.call_later(5, update, app, loop)

if __name__ == "__main__":
    APP = QtWidgets.QApplication(sys.argv)
    LOOP = quamash.QEventLoop(APP)
    asyncio.set_event_loop(LOOP)
    MYAPP = gui.main_window.MainWindow()
    MYAPP.show()
    with LOOP:
        LOOP.call_soon(update, MYAPP, LOOP)
        LOOP.run_forever()

