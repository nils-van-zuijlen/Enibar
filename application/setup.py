# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
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
Will insert 100 fake notes in the db.
"""

from api import notes
import faker
import time
import random
import datetime

FAK = faker.Faker()

for i in range(100):
    id_ = notes.add(FAK.first_name(), FAK.first_name(), FAK.first_name(),
                    FAK.email(), FAK.phone_number(),
                    datetime.datetime.fromtimestamp(
                        random.randint(int(time.time() - 36 * 365 * 3600 * 24),
                                       int(time.time()))).strftime("%d/%m/%Y"),
                    "1A", "")
    notes.transaction(id_, random.randint(-10, 10))

