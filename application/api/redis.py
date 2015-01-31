import asyncio
import asyncio_redis
import json
import settings

connection = None


def connect():
    global connection
    connection = yield from asyncio_redis.Pool.create(settings.HOST, 6379, poolsize=10)


def send_message(channel, message):
    asyncio.async(connection.publish(channel, json.dumps(message)))


def get_key(key, callback):
    value = ""
    loop = asyncio.get_event_loop()
    def wrapper():
        nonlocal value
        transport, protocol = yield from loop.create_connection(asyncio_redis.RedisProtocol, settings.HOST, 6379)
        value = yield from protocol.get(key)
        callback(value)
    asyncio.async(wrapper())


def set_key(key, value, callback):
    loop = asyncio.get_event_loop()
    def wrapper():
        transport, protocol = yield from loop.create_connection(asyncio_redis.RedisProtocol, settings.HOST, 6379)
        yield from protocol.set(key, value)
        callback()
    asyncio.async(wrapper())

