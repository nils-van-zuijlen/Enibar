import aiohttp
import api.notes
import api.redis
import asyncio
import settings
import json


QUEUE_NAME = "enibar-queue-sde"


class QueueProcessingException(Exception):
    pass


async def send_notes(notes):
    print("Adding notes: ", notes)
    for note in api.notes.get(lambda n: n['nickname'] in notes):
        req = {"type": "note", "id": note["id"], "nickname": note["nickname"],
            "mail": note["mail"], "note": note["note"]}
        async with api.redis.connection.get() as redis:
            await redis.rpush(QUEUE_NAME, json.dumps(req))


async def send_note_deletion(notes_id):
    print("Deleting note: ", notes_id)
    for note_id in notes_id:
        req = {"type": "note-delete", "id": note_id}
        async with api.redis.connection.get() as redis:
            await redis.rpush(QUEUE_NAME, json.dumps(req))


async def process_queue():
    async with api.redis.connection.get() as redis:
        while True:
            try:
                item = await redis.blpop(QUEUE_NAME)
                await _process_queue_item(item[1])
            except asyncio.CancelledError:
                break
            except Exception as e:
                print("Error in queue processing: ", e)
                await redis.lpush(QUEUE_NAME, item[1])
                await asyncio.sleep(60)


async def _process_queue_item(item):
    parsed_item = json.loads(item.decode())
    type_ = parsed_item.pop('type')
    print("Processing: ", item)
    if type_.endswith('-delete'):
        async with aiohttp.delete(settings.WEB_URL + type_[:-7], data=json.dumps(parsed_item)) as req:
            if req.status != 200:
                raise QueueProcessingException(req.status)
    else:
        async with aiohttp.put(settings.WEB_URL + type_, data=json.dumps(parsed_item)) as req:
            if req.status != 200:
                raise QueueProcessingException(req.status)

