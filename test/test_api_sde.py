import basetest
import api.redis
import asyncio
import json
import settings


settings.WEB_URL = 'http://127.0.0.1:52412/'


class MockSdeServer(asyncio.Protocol):
    received = None

    def connection_made(self, transport):
        self.transport = transport
        self.to_send = b"HTTP/1.1 200 OK\r\n\r\n"

    def data_received(self, data):
        message = data.decode()
        MockSdeServer.received = message

        self.transport.write(self.to_send)

        self.transport.close()


class MockBadSdeServer(MockSdeServer):
    def connection_made(self, transport):
        super().connection_made(transport)
        self.to_send = b"HTTP/1.1 500 OK\r\n\r\n"


class ApiSdeTests(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        for i in range(3):
            name = "test" + str(i)
            api.notes.add(name,
                name,
                name,
                name + "@pouette.com",
                "0600000000",
                '12/12/2001',
                '1A',
                '',
                True,
                True
            )
            api.notes.transactions(["test" + str(i)], -i)
            api.notes.rebuild_cache()
        self.loop = asyncio.get_event_loop()
        settings.USE_PROXY = False

    def test_sde_add_note(self):
        """ Testing adding a note to the queue
        """
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_notes(["test1", "test2"])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{"token": "changeme", "id": 3, "type": "note", "note": -2.0, "mail": "test2@pouette.com", "nickname": "test2"}, {"token": "changeme", "id": 2, "type": "note", "note": -1.0, "mail": "test1@pouette.com", "nickname": "test1"}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

    def test_sde_delete_note(self):
        """ Testing deleting a note from the queue
        """
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_note_deletion([1, 2])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{"token": "changeme", 'id': 1, 'type': 'note-delete'}, {"token": "changeme", 'id': 2, 'type': 'note-delete'}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

    def test_sde_add_history_lines(self):
        """ Testing adding an history line to the queue
        """
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_history_lines(
                    [{"price_name": "test", "note": "test1", "category": "test", "price": -0.8, "quantity": 2, "product": "test", "id": 1},
                    {"price_name": "test3", "note": "test3", "category": "test3", "price": -0.7, "quantity": 1, "product": "test3", "id": 3}])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{"token": "changeme", 'type': 'history', 'category': 'test', 'price': -0.8, 'id': 1, 'price_name': 'test', 'quantity': 2, 'note': 'test1', 'product': 'test'}, {"token": "changeme", 'type': 'history', 'category': 'test3', 'price': -0.7, 'id': 3, 'price_name': 'test3', 'quantity': 1, 'note': 'test3', 'product': 'test3'}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

    def test_sde_delete_history_line(self):
        """ Testing deleting an history line from the queue
        """
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_history_deletion([1, 2])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{"token": "changeme", 'id': 1, 'type': 'history-delete'}, {"token": "changeme", 'id': 2, 'type': 'history-delete'}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

    def test_sde_process_queue_item(self):
        """ Testing processing one item of the queue
        """
        async def test_func():
            await api.sde._process_queue_item(b'{"token": "changeme", "id": 1, "type": "history-delete"}')
            msg = MockSdeServer.received.split('\r\n')
            self.assertEqual(msg[0], 'DELETE /history HTTP/1.1')
            self.assertEqual(json.loads(msg[-1]), {"token": "changeme", "id": 1})
            await api.sde._process_queue_item(b'{"token": "changeme", "id": 3, "type": "note", "note": -2.0, "mail": "test2@pouette.com", "nickname": "test2"}')
            msg = MockSdeServer.received.split('\r\n')
            self.assertEqual(msg[0], 'PUT /note HTTP/1.1')
            self.assertEqual(json.loads(msg[-1]), {"token": "changeme", "id": 3, "mail": "test2@pouette.com", "nickname": "test2", "note": -2.0})
        coro = self.loop.create_server(MockSdeServer, '127.0.0.1', 52412)
        server = self.loop.run_until_complete(coro)
        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)
        server.close()
        self.loop.run_until_complete(server.wait_closed())

    def test_sde_process_queue_item_without_server(self):
        """ Testing processing one item of the queue without a server
        """
        async def test_func():
            with self.assertRaises(Exception):
                await api.sde._process_queue_item(b'{"token": "changeme", "id": 1, "type": "history-delete"}')
        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)

    def test_sde_process_queue_item_with_bad_server(self):
        """ Testing processing one item of the queue with a bad server
        """
        async def test_func():
            with self.assertRaises(api.sde.QueueProcessingException):
                await api.sde._process_queue_item(b'{"token": "changeme", "id": 1, "type": "history-delete"}')
            with self.assertRaises(api.sde.QueueProcessingException):
                await api.sde._process_queue_item(b'{"token": "changeme", "id": 3, "type": "note", "note": -2.0, "mail": "test2@pouette.com", "nickname": "test2"}')
        coro = self.loop.create_server(MockBadSdeServer, '127.0.0.1', 52412)
        server = self.loop.run_until_complete(coro)
        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)
        server.close()
        self.loop.run_until_complete(server.wait_closed())

    def test_sde_process_queue(self):
        """ Testing processing a full queue
        """
        async def test_func():
            await api.sde.send_note_deletion([1, 2])
            task = asyncio.ensure_future(api.sde.process_queue())
            await asyncio.sleep(1)
            task.cancel()
            async with api.redis.connection.get() as redis:
                res = await redis.lpop(api.sde.QUEUE_NAME)
                self.assertIsNone(res)
        coro = self.loop.create_server(MockSdeServer, '127.0.0.1', 52412)
        server = self.loop.run_until_complete(coro)
        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)
        server.close()
        self.loop.run_until_complete(server.wait_closed())

    def test_sde_process_queue_with_bad_server(self):
        """ Testing processing a full queue with bad server
        """
        async def test_func():
            await api.sde.send_note_deletion([1])
            task = asyncio.ensure_future(api.sde.process_queue())
            await asyncio.sleep(1)
            task.cancel()
            async with api.redis.connection.get() as redis:
                res = await redis.lpop(api.sde.QUEUE_NAME)
                self.assertEqual(json.loads(res.decode()), {"token": "changeme", "id": 1, "type": "note-delete"})
        coro = self.loop.create_server(MockBadSdeServer, '127.0.0.1', 52412)
        server = self.loop.run_until_complete(coro)
        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)
        server.close()
        self.loop.run_until_complete(server.wait_closed())

    def test_sde_connection_with_proxy(self):
        settings.USE_PROXY = True
        settings.PROXY_AUTH = "http://test:test@127.0.0.1:3222"
        async def test_func():
            await api.sde.send_notes(["test1"])
            task = asyncio.ensure_future(api.sde.process_queue())
            await asyncio.sleep(1)
            task.cancel()
            msg = MockSdeServer.received.split('\r\n')
            self.assertEqual(msg[0], 'PUT http://127.0.0.1:52412/note HTTP/1.1')

        coro = self.loop.create_server(MockSdeServer, '127.0.0.1', 3222)
        server = self.loop.run_until_complete(coro)

        task = asyncio.ensure_future(test_func())
        self.loop.run_until_complete(task)

        server.close()
        self.loop.run_until_complete(server.wait_closed())
