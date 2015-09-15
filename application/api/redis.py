import asyncio
import aioredis
import json
import settings

connection = None


def connect():
    global connection
    connection = yield from aioredis.create_pool((settings.HOST, 6379), maxsize=10)


def send_message(channel, message):
    def wrapper():
        with (yield from connection) as redis:
            yield from redis.publish_json(channel, message)
    asyncio.async(wrapper())


def get_key(key, callback):
    global connection
    value = ""
    loop = asyncio.get_event_loop()

    def wrapper():
        nonlocal value
        with (yield from connection) as redis:
            value = yield from redis.get(key)
        callback(value.decode())
    asyncio.async(wrapper())


def set_key(key, value, callback):
    loop = asyncio.get_event_loop()

    def wrapper():
        with (yield from connection) as redis:
            yield from redis.set(key, value)
        callback()
    asyncio.async(wrapper())

