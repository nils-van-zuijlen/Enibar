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
import asyncio
import api.redis
import asyncio
import basetest
import functools
import imp
import sys
import time
import uuid
from PyQt5 import QtCore, QtWidgets


def give_random_key(func):
    @functools.wraps(func)
    def test_inner(self):
        key = uuid.uuid4().hex
        func(self, key)
    return test_inner


class RedisTest(basetest.BaseTest):
    def setUp(self):
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

    @give_random_key
    def test_locking(self, key):
        self.assertFalse(api.redis.blocking_connection.exists(key))
        self.assertEqual(api.redis.LOCKS, {})
        self.assertTrue(api.redis.lock(key, 10))
        self.assertEqual(api.redis.LOCKS, {key: 10})
        self.assertTrue(api.redis.blocking_connection.exists(key))
        self.assertFalse(api.redis.lock(key, 10))

    @give_random_key
    def test_relocking(self, key):
        self.assertTrue(api.redis.lock(key, 1))
        time.sleep(0.9)
        api.redis._renew_lock(key, 1)
        time.sleep(0.2)
        # With a TTL of 1 second and a renewal after 0.9, the lock should still
        # be held
        self.assertFalse(api.redis.lock(key, 1))
        time.sleep(0.7)
        api.redis._renew_locks()
        time.sleep(0.2)
        self.assertFalse(api.redis.lock(key, 1))

    @give_random_key
    def test_expiring_lock(self, key):
        self.assertTrue(api.redis.lock(key, 1))
        time.sleep(1)
        # TODO: Warning ?
        self.assertTrue(api.redis.lock(key, 1))

    @give_random_key
    def test_unlocking(self, key):
        self.assertTrue(api.redis.lock(key, 1))
        api.redis.unlock(key)
        self.assertEqual(api.redis.LOCKS, {})
        self.assertTrue(api.redis.lock(key, 1))

    @give_random_key
    def test_unlocking_non_locked_key(self, key):
        with self.assertRaises(api.redis.LockingException):
            api.redis.unlock(key)

    @give_random_key
    def test_ping_redis(self, key):
        api.redis.PING_TIME = 0.5  # We don't want tests to take forever...
        self.assertTrue(api.redis.lock(key, 1))

        async def wait_2s():
            await asyncio.sleep(2)

        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(api.redis.ping_redis())
        loop.run_until_complete(asyncio.ensure_future(wait_2s()))

        self.assertFalse(api.redis.lock(key, 1))
