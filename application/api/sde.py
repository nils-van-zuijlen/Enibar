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
    for note in api.notes.get(lambda n: n['nickname'] in notes):
        req = {
            "token": settings.AUTH_SDE_TOKEN,
            "type": "note",
            "id": note["id"],
            "nickname": note["nickname"],
            "mail": note["mail"],
            "note": note["note"]}
        with await api.redis.connection as redis:
            await redis.rpush(QUEUE_NAME, json.dumps(req))


async def send_note_deletion(notes_id):
    for note_id in notes_id:
        req = {"token": settings.AUTH_SDE_TOKEN, "type": "note-delete", "id": note_id}
        with await api.redis.connection as redis:
            await redis.rpush(QUEUE_NAME, json.dumps(req))


async def send_history_lines(lines):
    with await api.redis.connection as redis:
        for line in lines:
            try:
                line.pop("deletable")
            except KeyError:
                pass
            line["type"] = "history"
            line["token"] = settings.AUTH_SDE_TOKEN
            await redis.rpush(QUEUE_NAME, json.dumps(line))


async def send_history_deletion(lines_id):
    for line_id in lines_id:
        req = {"token": settings.AUTH_SDE_TOKEN, "type": "history-delete", "id": line_id}
        with await api.redis.connection as redis:
            await redis.rpush(QUEUE_NAME, json.dumps(req))


async def process_queue():
    with await api.redis.connection as redis:
        while True:
            try:
                item = await redis.blpop(QUEUE_NAME)
                await _process_queue_item(item[1])
            except asyncio.CancelledError:
                redis.close()
                return
            except Exception as e:
                print(e)
                await redis.lpush(QUEUE_NAME, item[1])
                await asyncio.sleep(60)


async def _process_queue_item(item):
    parsed_item = json.loads(item.decode())
    parsed_item['token'] = settings.AUTH_SDE_TOKEN
    type_ = parsed_item.pop('type')
    if settings.USE_PROXY:
        proxy = settings.PROXY_AUTH
    else:
        proxy = None
    if type_.endswith('-delete'):
        async with aiohttp.ClientSession() as session:
            async with session.delete(settings.WEB_URL + type_[:-7],
                                      data=json.dumps(parsed_item),
                                      proxy=proxy) as req:
                if req.status != 200:
                    raise QueueProcessingException(req.status)
    else:
        async with aiohttp.ClientSession() as session:
            async with session.put(settings.WEB_URL + type_,
                                   data=json.dumps(parsed_item),
                                   proxy=proxy) as req:
                if req.status != 200:
                    raise QueueProcessingException(req.status)
