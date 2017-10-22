#!/bin/env python3

import getpass
import redis
import os
import sys
from PyQt5 import QtSql


dir_path = os.path.dirname(os.path.realpath(__file__))

CONFIG = {
    "DEBUG": False,
    "IMG_BASE_DIR": "img/",
    "MAX_HISTORY": 5,
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PASSWORD": None,
}

redis_ip = input("Redis IP > ")
redis_password = getpass.getpass("Redis password (empty if none)> ")

rs = redis.StrictRedis(redis_ip, password=redis_password)

try:
    rs.get(None)
    CONFIG["REDIS_HOST"] = redis_ip
    CONFIG["REDIS_PASSWORD"] = redis_password
except:
    print("Your redis credentials are wrong, please check them and try again")
    sys.exit()

should_config_db = input("Should I configure the db too (is unsure, say n) [y/N] > ")

if should_config_db.lower() == "y":
    db_host = input("Database host > ")
    db_user = input("Database username > ")
    db_password = getpass.getpass("Database password > ")
    db_name = input("Database name > ")

    database = QtSql.QSqlDatabase("QPSQL")
    database.setHostName(db_host)
    database.setUserName(db_user)
    database.setPassword(db_password)
    database.setDatabaseName(db_name)
    if not database.open():
        print("Your postgres credentials are wrong, please check them and try again")
        sys.exit()

    rs.set("DB_HOST", db_host)
    rs.set("USERNAME", db_user)
    rs.set("PASSWORD", db_password)
    rs.set("DBNAME", db_name)

with open(os.path.join(dir_path, "../application/local_settings.py"), "w") as fd:
    fd.write("%s = %s\n" % ("DEBUG", CONFIG["DEBUG"]))
    fd.write("%s = \"%s\"\n" % ("IMG_BASE_DIR", CONFIG["IMG_BASE_DIR"]))
    fd.write("%s = %s\n" % ("MAX_HISTORY", CONFIG["MAX_HISTORY"]))
    fd.write("%s = \"%s\"\n" % ("REDIS_HOST", CONFIG["REDIS_HOST"]))
    if CONFIG['REDIS_PASSWORD']:
        fd.write("%s = \"%s\"\n" % ("REDIS_PASSWORD", CONFIG["REDIS_PASSWORD"]))
    else:
        fd.write("%s = %s\n" % ("REDIS_PASSWORD", "None"))
