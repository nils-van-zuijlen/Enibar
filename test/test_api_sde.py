import basetest
import api.redis
import asyncio
import json


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
        self.loop.run_until_complete(api.redis.connect())

    def test_sde_add_note(self):
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_notes(["test1", "test2"])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{"id": 3, "type": "note", "note": -2.0, "mail": "test2@pouette.com", "nickname": "test2"}, {"id": 2, "type": "note", "note": -1.0, "mail": "test1@pouette.com", "nickname": "test1"}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

    def test_sde_delete_note(self):
        async def func_test():
            async with api.redis.connection.get() as redis:
                await redis.delete(api.sde.QUEUE_NAME)
                await api.sde.send_note_deletion([1, 2])

                total = []
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                res = await redis.blpop(api.sde.QUEUE_NAME)
                total.append(json.loads(res[1].decode()))
                self.assertCountEqual(total, [{'id': 1, 'type': 'note-delete'}, {'id': 2, 'type': 'note-delete'}])

        task = asyncio.ensure_future(func_test())
        self.loop.run_until_complete(task)

