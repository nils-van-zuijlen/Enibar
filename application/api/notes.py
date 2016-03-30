# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
#
# This file is part of Enibar.
#
# Enibar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Enibar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

"""
Notes
=====

"""

from PyQt5 import QtSql
import api.transactions
import api.redis
from database import Cursor, Database
import datetime
import os.path
import settings
import shutil
import tempfile


NOTE_FIELDS = ['id', 'nickname', 'lastname', 'firstname', 'mail', 'tel',
               'birthdate', 'promo', 'note', 'photo_path', 'overdraft_date',
               'ecocups', 'hidden', 'mails_inscription', 'stats_inscription']

NOTES_CACHE = {}
NOTES_FIELDS_CACHE = {}
NOTES_STATS_FIELDS_CACHE = {}


def rebuild_cache():
    """ Build a cache with all notes inside. This improve greatly the perfs of
        get actions
    """
    global NOTES_CACHE, NOTES_FIELDS_CACHE
    NOTES_CACHE = {}
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes")
        if cursor.exec_():
            while cursor.next():
                record = cursor.record()
                if NOTES_FIELDS_CACHE == {}:
                    NOTES_FIELDS_CACHE = {field: record.indexOf(field) for field
                                          in NOTE_FIELDS}
                row = {field: record.value(NOTES_FIELDS_CACHE[field]) for field
                       in NOTE_FIELDS}
                row['tot_cons'] = 0
                row['tot_refill'] = 0
                NOTES_CACHE[row['nickname']] = row
    _build_stats()


def _build_stats():
    """ Add stats to the notes in the cache.
    """
    global NOTES_STATS_FIELDS_CACHE
    with Cursor() as cursor:
        cursor.prepare("SELECT nickname, notes.firstname, notes.lastname,\
                        SUM(IF(price>0, price, 0)) as tot_refill,\
                        SUM(IF(price<0, price, 0)) AS tot_cons\
                        FROM transactions INNER JOIN notes ON\
                        notes.firstname=transactions.firstname AND\
                        notes.lastname=transactions.lastname\
                        GROUP BY firstname, lastname")

        if cursor.exec_():
            tot = {}
            while cursor.next():
                record = cursor.record()
                if NOTES_STATS_FIELDS_CACHE == {}:
                    NOTES_STATS_FIELDS_CACHE = {field: record.indexOf(field)
                                                for field in ('lastname',
                                                              'nickname',
                                                              'firstname',
                                                              'tot_cons',
                                                              'tot_refill'
                                                             )
                                               }

                note = record.value(NOTES_STATS_FIELDS_CACHE['nickname'])
                tot[note] = {}
                NOTES_CACHE[note]['tot_cons'] = record.value(NOTES_STATS_FIELDS_CACHE['tot_cons'])
                NOTES_CACHE[note]['tot_refill'] = record.value(NOTES_STATS_FIELDS_CACHE['tot_refill'])


def rebuild_note_cache(nick):
    """ Rebuild a row in the cache
    """
    global NOTES_CACHE, NOTES_FIELDS_CACHE, NOTES_STATS_FIELDS_CACHE
    with Cursor() as cursor:
        cursor.prepare("SELECT * FROM notes WHERE nickname=:nick")
        cursor.bindValue(":nick", nick)
        if cursor.exec_():
            while cursor.next():
                record = cursor.record()
                if NOTES_FIELDS_CACHE == {}:
                    NOTES_FIELDS_CACHE = {field: record.indexOf(field) for field
                                          in NOTE_FIELDS}
                row = {field: record.value(NOTES_FIELDS_CACHE[field]) for field
                       in NOTE_FIELDS}
                row['tot_cons'] = 0.0
                row['tot_refill'] = 0.0

                NOTES_CACHE[row['nickname']] = row

                with Cursor() as cursor:
                    cursor.prepare("SELECT nickname, notes.firstname, notes.lastname,\
                                    SUM(IF(price>0, price, 0)) as tot_refill,\
                                    SUM(IF(price<0, price, 0)) AS tot_cons\
                                    FROM transactions INNER JOIN notes ON\
                                    notes.firstname=transactions.firstname AND\
                                    notes.lastname=transactions.lastname\
                                    WHERE notes.firstname=:fn AND notes.lastname=:ln\
                                    GROUP BY firstname, lastname")
                    cursor.bindValue(':fn', row['firstname'])
                    cursor.bindValue(':ln', row['lastname'])

                    if cursor.exec_():
                        while cursor.next():
                            record = cursor.record()
                            if NOTES_STATS_FIELDS_CACHE == {}:
                                NOTES_STATS_FIELDS_CACHE = {field: record.indexOf(field)
                                                            for field in ('lastname',
                                                                          'nickname',
                                                                          'firstname',
                                                                          'tot_cons',
                                                                          'tot_refill'
                                                                         )
                                                           }

                            note = record.value(NOTES_STATS_FIELDS_CACHE['nickname'])
                            NOTES_CACHE[note]['tot_cons'] = record.value(NOTES_STATS_FIELDS_CACHE['tot_cons'])
                            NOTES_CACHE[note]['tot_refill'] = record.value(NOTES_STATS_FIELDS_CACHE['tot_refill'])


def _request_multiple_nicks(nicks, request, *, do_not=False):
    """ Execute the request on multiple notes

    :param list nicks: Nicknames of the notes on wich the request\
    will be executed
    :param str request: The request
    """

    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare(request)
        for nick in nicks:
            cursor.bindValue(':nick', nick)
            cursor.exec_()
        value = database.commit()
    return value


def change_values(nick, *, do_not=False, **kwargs):
    """ Change the value of the columns for the note with the nickname
        `nickname`
    """
    with Cursor() as cursor:
        setter = ", ".join("{key}=:{key}".format(key=key) for key in kwargs)
        cursor.prepare("UPDATE notes SET {} WHERE nickname=:nick".format(
            setter))
        for key, value in kwargs.items():
            cursor.bindValue(':{}'.format(key), value)
        cursor.bindValue(':nick', nick)
        value = cursor.exec_()
    if 'nickname' in kwargs:  # Note renaming
        api.redis.send_message("enibar-delete", [nick, ])
        api.redis.send_message("enibar-notes", [kwargs['nickname'], ])
    else:
        api.redis.send_message("enibar-notes", [nick, ])
    return value


def unique_file(file_name):
    """ Return an unique filename
    """
    dirname, filename = os.path.split(file_name)
    prefix, suffix = os.path.splitext(filename)

    _, filename = tempfile.mkstemp(suffix, prefix + "_", dirname)
    return filename


def add(nickname, firstname, lastname, mail, tel, birthdate, promo, photo_path,
        stats_inscription, mails_inscription):
    """ Create a note. Copy the image from photo_path to settings.IMG_BASE_DIR

    :param str nickname: Nickname
    :param str lastname: Last name
    :param str firstname: First name
    :param str mail: Mail
    :param str tel: Phone number
    :param int birthdate: Birthday (DD/MM/YYYY)
    :param str promo: Promo. One of '1A', '2A', '3A', '3S', '4A', '5A',\
    'Ancien', 'Prof', 'Externe', Esiab'
    :param str photo_path: The path of the photo to use.

    :return bool: The id of the note created or -1.
    """
    if photo_path:
        name = os.path.split(photo_path)[1]
        if name:
            if os.path.exists(settings.IMG_BASE_DIR + name):
                name = os.path.split(unique_file(settings.IMG_BASE_DIR +
                                                 name))[1]
            shutil.copyfile(photo_path, settings.IMG_BASE_DIR + name)

    with Cursor() as cursor:
        cursor.prepare("INSERT INTO notes (nickname, lastname, firstname,\
                        mail, tel, birthdate, promo, photo_path,\
                        mails_inscription, stats_inscription)\
                        VALUES(:nickname, :lastname, :firstname, :mail, :tel,\
                        :birthdate, :promo, :photo_path, :mails_inscription,\
                        :stats_inscription)")
        birthdate = datetime.datetime.strptime(birthdate,
                                               "%d/%m/%Y").timestamp()

        cursor.bindValues({':nickname': nickname, ':lastname': lastname,
                           ':firstname': firstname, ':mail': mail, ':tel': tel,
                           ':birthdate': birthdate, ':promo': promo,
                           ':photo_path': name if photo_path else "",
                           ':mails_inscription': mails_inscription,
                           ':stats_inscription': stats_inscription})

        if cursor.exec_():
            api.redis.send_message("enibar-notes", [nickname, ])
            return cursor.lastInsertId()
        return -1


def remove(nicks):
    """ Remove a list of notes

    :param list nicks: The list of notes to delete

    :return bool: True if success else False.
    """
    nicks = list(nicks)
    trs = []
    for nick in nicks:
        note = get(lambda x: x['nickname'] == nick)[0]
        trs.append({
            'note': nick,
            'category': "Note",
            'product': "",
            'price_name': "Fermeture",
            'quantity': "1",
            'liquid_quantity': 0,
            'percentage': 0,
            'price': -note['note']}
        )

    api.redis.send_message("enibar-delete", nicks)
    _request_multiple_nicks(nicks, "DELETE FROM notes WHERE nickname=:nick")
    api.transactions.log_transactions(trs)


def change_photo(nickname, new_photo):
    """ Change a note photo.

    :param str nickname: The nickname of the note.
    :param str new_path: The new photo_path

    :return bool: True if success else False
    """
    name = os.path.split(new_photo)[1]
    if name:
        if os.path.exists(settings.IMG_BASE_DIR + name):
            name = os.path.split(unique_file(settings.IMG_BASE_DIR +
                                             name))[1]
        shutil.copyfile(new_photo, settings.IMG_BASE_DIR + name)
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET photo_path=:photo_path \
                        WHERE nickname=:nickname")
        cursor.bindValues({':photo_path': name, ':nickname': nickname})
        value = cursor.exec_()
        api.redis.send_message("enibar-notes", [nickname, ])
    return value


def get(filter_function=None):
    """ Get notes with a filter. filter_function should be a function like \
            `lamda x: x["id"] == 1` \
        to keep only notes with the id 1

        :param callable filter_function: The filter to apply.
    """
    if filter_function is None:
        return list(NOTES_CACHE.values())
    return list(filter(filter_function, NOTES_CACHE.values()))


def hide(nicks):
    """ Hide multiple notes.

    :param list nicks: The list of notes to hide

    :return bool: True if success else False
    """
    v = _request_multiple_nicks(nicks, "UPDATE notes SET hidden=1\
        WHERE nickname=:nick")
    api.redis.send_message("enibar-notes", nicks)
    return v


def show(nicks):
    """ Show multiple notes

    :param int nicks: The list of notes to show

    :return bool: True if success else False
    """
    v = _request_multiple_nicks(nicks, "UPDATE notes SET hidden=0\
        WHERE nickname=:nick")
    api.redis.send_message("enibar-notes", nicks)
    return v


def transactions(notes, diff, *, do_not=False):
    """ Change the note on multiple notes

        :param str nickname: The nickname of the note
        :param float diff: Will add the diff to the note.

        :return bool: True if success else False
    """
    with Database() as database:
        database.transaction()
        cursor = QtSql.QSqlQuery(database)
        cursor.prepare("UPDATE notes SET note=note+:diff WHERE nickname=:nick")
        for nick in notes:
            cursor.bindValue(':nick', nick)
            cursor.bindValue(':diff', diff)
            cursor.exec_()
        value = database.commit()
    if not do_not:
        api.redis.send_message("enibar-notes", notes)
    return value


def change_ecocups(nick, diff, do_not=False):
    """ Change the number of ecocups taken on a note.

        :param str nick: The nickname og the note
        :param int diff: The number of ecocups to add.
    """
    with Cursor() as cursor:
        cursor.prepare("UPDATE notes SET ecocups=ecocups+:diff WHERE\
                        nickname=:nick")
        cursor.bindValue(":diff", diff)
        cursor.bindValue(":nick", nick)
        value = cursor.exec_()
    api.redis.send_message("enibar-notes", [nick, ])
    return value


def export(notes):
    """ Return an csv representation of all notes

        :param list: A list of notes to export
    """
    to_export = ["nickname", "firstname", "lastname", "note", "mail",
                 "photo_path"]
    csv = ", ".join(to_export)
    for note in notes:
        csv += "\n" + ",".join(str(note[value]) for value in to_export)
    return csv


def export_by_nick(notes_nicks, *args, **kwargs):
    """ Export notes but taking nicknames.
    """
    notes_nicks = list(notes_nicks)
    return export([note for note in NOTES_CACHE.values() if note['nickname'] in notes_nicks],
                  *args,
                  **kwargs)


def import_csv(notes, reason, amount, *, do_not=False):
    """ Import a csv file. There are no checks done here.
    CSV pattern: Nom,Prenom,Surnom,Note,Email,Date de naissance,Majeur,Debit,Motif

    Returns the number of line executed.
    """
    trs = []
    for note in notes:
        trs.append({
            'note': note,
            'category': "CSV import",
            'product': reason,
            'price_name': "Solde",
            'quantity': "1",
            'liquid_quantity': 0,
            'percentage': 0,
            'price': amount}
        )
    if transactions(notes, amount):
        if api.transactions.log_transactions(trs):
            return len(trs)


rebuild_cache()

