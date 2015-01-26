import asyncio
import asyncio_redis
import json
import settings

connection = None


def connect():
    global connection
    connection = yield from asyncio_redis.Connection.create(settings.HOST, 6379)


def send_message(channel, message):
    asyncio.async(connection.publish(channel, json.dumps(message)))

