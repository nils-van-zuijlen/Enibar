import asyncio
import asyncio_redis
import json

connection = None


def connect():
    global connection
    connection = yield from asyncio_redis.Connection.create('localhost', 6379)


def send_message(channel, message):
    asyncio.async(connection.publish(channel, json.dumps(message)))

