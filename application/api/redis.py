import settings
import asyncio
import aioredis
import json
import redis

connection = None
blocking_connection = redis.StrictRedis(host=settings.HOST, port=6379, db=0)


async def connect():
    global connection
    connection = await aioredis.create_pool((settings.HOST, 6379), maxsize=10)


def send_message(channel, message):
    async def wrapper():
        async with connection.get() as redis:
            await redis.publish_json(channel, message)
    asyncio.ensure_future(wrapper())


def get_key(key, callback):
    async def wrapper():
        async with connection.get() as redis:
            value = await redis.get(key)
        try:
            callback(value.decode())
        except:
            callback(value)
    asyncio.ensure_future(wrapper())


def set_key(key, value, callback):
    async def wrapper():
        async with connection.get() as redis:
            await redis.set(key, value)
        callback()
    asyncio.ensure_future(wrapper())


def get_key_blocking(key, default=None):
    return blocking_connection.get(key) or str(default).encode()


def set_key_blocking(key, value):
    blocking_connection.set(key, value)


async def ping_redis():
    while True:
        async with connection.get() as redis:
            await redis.ping()
        await asyncio.sleep(10)
