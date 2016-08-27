# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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

import aioredis
import sys
import api.redis
import imp
import asyncio
import basetest


class RedisTest(basetest.BaseTest):
    def setUp(self):
        # We need to reset api.redis because we overwrite it in some tests
        imp.reload(api.redis)
        super().setUp()

    def test_send_message(self):
        async def func():
            SUB = await aioredis.create_redis(("127.0.0.1", 6379))
            res = await SUB.psubscribe("enibar-*")
            subscriber = res[0]

            api.redis.send_message('enibar-test', 'test')

            await subscriber.wait_message()
            reply = await subscriber.get_json()
            self.assertEqual(reply, (b'enibar-test', 'test'))

        task = asyncio.ensure_future(func())
        self.loop.run_until_complete(task)

    def test_set_get_value(self):
        async def func():
            set_called = False
            get_bytes_called = False

            def callback_check_bytes(value):
                nonlocal get_bytes_called
                self.assertEqual(value, b"coucou")
                get_bytes_called = True

            def callback_set():
                nonlocal set_called
                set_called = True

            api.redis.set_key("test", "coucou", callback_set)
            api.redis.get_key("test", callback_check_bytes)

            await asyncio.sleep(0.1)
            self.assertTrue(set_called)
            self.assertTrue(get_bytes_called)

        task = asyncio.ensure_future(func())
        self.loop.run_until_complete(task)


