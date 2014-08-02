"""
Will insert 100 fake notes in the db.
"""

import api.notes
import faker
import time
import random

FAK = faker.Faker()

for i in range(100):
    id_ = api.notes.add(FAK.first_name(), FAK.first_name(), FAK.first_name(),
                        FAK.email(), FAK.phone_number(),
                        random.randint(int(time.time() - 36 * 365 * 3600 * 24),
                                       int(time.time())),
                        "1A", "")
    api.notes.transaction(id_, random.randint(-10, 10))

