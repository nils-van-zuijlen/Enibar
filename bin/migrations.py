#!/bin/env python3

import argparse
import os
import sqlparse
import sys
import tempfile
from PyQt5 import QtSql
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../application")

import database  # nopep8
import settings  # nopep8


def create_migrations_table():
    with database.Cursor() as cursor:
        cursor.exec_("""CREATE TABLE IF NOT EXISTS __migrations (version SERIAL PRIMARY KEY)""")


def execute_sql_file(filename):
    """ Since mysql can't rollback any CREATE/ALTER/DROP instruction,
    do a full backup before starting the migration and if it fails, and reapply
    it if it fails
    """
    with database.Database() as db, open(filename) as fd:
        if not db.transaction():
            print("Failed to start the migration")
            sys.exit(1)

        cursor = QtSql.QSqlQuery(db)
        for statement in sqlparse.split(fd.read()):
            if not statement:
                continue

            if not cursor.exec_(statement):
                db.rollback()
                print(cursor.lastError().text())
                break
        else:
            db.commit()


def new_migration(name):
    # Get version from the last miration created
    version = -1
    for migration in os.listdir("../migrations"):
        version += 1
    version += 1
    print(f"Creating migration {version:0>5}_{name}")
    directory = f"../migrations/{version:0>5}_{name}"
    os.makedirs(directory)
    open(os.path.join(directory, "up.sql"), 'a').close()
    open(os.path.join(directory, "down.sql"), 'a').close()


def apply_migrations():
    # Get the latest applied migration
    with database.Cursor() as cursor:
        cursor.prepare("SELECT version FROM __migrations ORDER BY version DESC LIMIT 1")
        cursor.exec_()
        last_applied = -1
        if cursor.next():
            last_applied = cursor.value("version")

    migration_file, migration_name = tempfile.mkstemp()

    should_apply = False
    nb = 0
    for migration in sorted(os.listdir("../migrations")):
        nb = int(migration.split("_")[0])
        if nb <= last_applied:
            continue
        should_apply = True
        print(f"Applying {migration}")
        with open(os.path.join("../migrations", migration, "up.sql")) as fd:
            os.write(migration_file, fd.read().encode())
        os.write(migration_file, f"INSERT INTO __migrations(version) VALUES({nb});\n".encode())

    if not should_apply:
        print("Nothing to do")
        sys.exit(1)


    # Execute the generated file.
    execute_sql_file(migration_name)

    # Since mkstemp doesn't handle automatically the file deletion, do it
    # ourselves
    os.remove(migration_name)


def rollback_migrations():
    lower = -1
    upper = -1
    with database.Cursor() as cursor:
        cursor.prepare("SELECT version FROM __migrations ORDER BY version DESC LIMIT 2")
        cursor.exec_()
        if cursor.next():
            upper = int(cursor.value("version"))
        if cursor.next():
            lower = int(cursor.value("version"))

    should_apply = False

    migration_file, migration_name = tempfile.mkstemp()

    for migration in sorted(os.listdir("../migrations"), reverse=True):
        nb = int(migration.split("_")[0])
        if lower < nb <= upper:
            should_apply = True
            print(f"Rollback {migration}")
            with open(os.path.join("../migrations", migration, "down.sql")) as fd:
                os.write(migration_file, fd.read().encode())

    os.write(migration_file, f"DELETE FROM __migrations WHERE version={upper};\n".encode())

    if should_apply:
        execute_sql_file(migration_name)
    else:
        print("Nothing to do")
    os.remove(migration_name)


def print_help_and_exit():
    print('Usage: ./migrations.py {new [name], apply, rollback}')
    sys.exit(1)


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc < 2:
        print_help_and_exit()

    if sys.argv[1] not in ['apply', 'new', 'rollback']:
        print_help_and_exit()

    if sys.argv[1] == 'new' and argc != 3:
        print_help_and_exit()
    elif sys.argv[1] in ['apply', 'rollback'] and argc != 2:
        print_help_and_exit()

    # First make sure the migrations table exists
    create_migrations_table()

    # Then the migrations dir
    os.makedirs("../migrations", exist_ok=True)

    if sys.argv[1] == 'new':
        new_migration(sys.argv[2])
    elif sys.argv[1] == 'apply':
        apply_migrations()
    elif sys.argv[1] == 'rollback':
        rollback_migrations()

