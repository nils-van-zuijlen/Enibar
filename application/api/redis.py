import settings
import asyncio
import aioredis
import redis
import sys
import rapi
from PyQt5 import QtWidgets


connection = None
blocking_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0,
                                        password=settings.REDIS_PASSWORD)

try:
    blocking_connection.ping()
except redis.exceptions.ConnectionError:
    if rapi.utils.check_x11():
        # We need this to create an app before opening a window.
        import gui.utils
        tmp = QtWidgets.QApplication(sys.argv)
        gui.utils.error("Error", "Can't join redis")
    print("Can't join redis")
    sys.exit(5)

PING_TIME = 10


async def connect():
    global connection
    connection = await aioredis.create_redis_pool((settings.REDIS_HOST, 6379), maxsize=10,
                                                  password=settings.REDIS_PASSWORD)


def send_message(channel, message):
    async def wrapper():
        with await connection as redis:
            await redis.publish_json(channel, message)
    asyncio.ensure_future(wrapper())


def get_key(key, callback):
    async def wrapper():
        with await connection as redis:
            value = await redis.get(key)
        try:
            callback(value.decode())
        except:
            callback(value)
    asyncio.ensure_future(wrapper())


def set_key(key, value, callback):
    async def wrapper():
        with await connection as redis:
            await redis.set(key, value)
            callback()
    asyncio.ensure_future(wrapper())


def get_key_blocking(key, default=None):
    return blocking_connection.get(key) or str(default).encode()


def set_key_blocking(key, value):
    blocking_connection.set(key, value)


async def ping_redis():
    while True:
        with await connection as redis:
            await redis.ping()
            _renew_locks()
        await asyncio.sleep(PING_TIME)


class LockingException(Exception):
    pass


# This is all the we currently have and need to renew
# In the form {NAME: TTL}
LOCKS = {}


def lock(lock_name, ttl):
    if blocking_connection.exists(lock_name):
        return False
    LOCKS[lock_name] = ttl
    blocking_connection.set(lock_name, "", ttl)
    return True


def unlock(lock_name):
    if lock_name not in LOCKS:
        raise LockingException

    del LOCKS[lock_name]
    blocking_connection.delete(lock_name)


def _renew_lock(lock_name, ttl):
    blocking_connection.expire(lock_name, ttl)


def _renew_locks():
    for lock, ttl in LOCKS.items():
        _renew_lock(lock, ttl)
