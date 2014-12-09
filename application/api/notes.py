# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
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
from database import Cursor, Database
import datetime
import os.path
import settings
import shutil
import tempfile


NOTE_FIELDS = ['id', 'nickname', 'lastname', 'firstname', 'mail', 'tel',
               'birthdate', 'promo', 'note', 'photo_path', 'overdraft_date',
               'ecocups', 'hidden']

NOTES_CACHE = []
NOTES_FIELDS_CACHE = {}


def rebuild_cache():
    """ Build a cache with all notes inside. This improve greatly the perfs of
        get actions
    """
    global NOTES_CACHE, NOTES_FIELDS_CACHE
    NOTES_CACHE = []
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
                NOTES_CACHE.append(row)
        _build_stats()
    return True


def _build_stats():
    """ Add stats to the notes in the cache.
    """
    global NOTES_CACHE
    with Cursor() as cursor:
        cursor.prepare("SELECT note, SUM(IF(price>0, price, 0)) as tot_refill,\
                        SUM(IF(price<0, price, 0)) AS tot_cons\
                        FROM transactions GROUP BY note")
        if cursor.exec_():
            tot = {}
            while cursor.next():
                record = cursor.record()
                note = record.value('note')
                tot[note] = {}
                tot[note]['tot_cons'] = record.value('tot_cons')
                tot[note]['tot_refill'] = record.value('tot_refill')
            for note in NOTES_CACHE:
                if note['nickname'] in tot:
                    note['tot_cons'] = tot[note['nickname']]['tot_cons']
                    note['tot_refill'] = tot[note['nickname']]['tot_refill']


def _request_multiple_nicks(nicks, request):
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
    rebuild_cache()
    return value


def change_values(nick, **kwargs):
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
    rebuild_cache()
    return value


def unique_file(file_name):
    """ Return an unique filename
    """
    dirname, filename = os.path.split(file_name)
    prefix, suffix = os.path.splitext(filename)

    _, filename = tempfile.mkstemp(suffix, prefix + "_", dirname)
    return filename


def add(nickname, firstname, lastname, mail, tel, birthdate, promo, photo_path):
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
                        mail, tel, birthdate, promo, photo_path)\
                        VALUES(:nickname, :lastname, :firstname, :mail, :tel,\
                        :birthdate, :promo, :photo_path)")
        birthdate = datetime.datetime.strptime(birthdate,
                                               "%d/%m/%Y").timestamp()

        cursor.bindValues({':nickname': nickname, ':lastname': lastname,
                           ':firstname': firstname, ':mail': mail, ':tel': tel,
                           ':birthdate': birthdate, ':promo': promo,
                           ':photo_path': name if photo_path else ""})

        if cursor.exec_():
            rebuild_cache()
            return cursor.lastInsertId()
        return -1


def remove(nicks):
    """ Remove a list of notes

    :param list nicks: The list of notes to delete

    :return bool: True if success else False.
    """
    _request_multiple_nicks(nicks, "DELETE FROM notes WHERE nickname=:nick")


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
    rebuild_cache()
    return value


def get(filter_function=None):
    """ Get notes with a filter. filter_function should be a function like \
            `lamda x: x["id"] == 1` \
        to keep only notes with the id 1

        :param callable filter_function: The filter to apply.
    """
    if filter_function is None:
        return NOTES_CACHE
    rows = []
    for row in NOTES_CACHE:
        if filter_function(row):
            rows.append(row)
    return rows


def hide(nicks):
    """ Hide multiple notes.

    :param list nicks: The list of notes to hide

    :return bool: True if success else False
    """
    return _request_multiple_nicks(nicks, "UPDATE notes SET hidden=1\
        WHERE nickname=:nick")


def show(nicks):
    """ Show multiple notes

    :param int nicks: The list of notes to show

    :return bool: True if success else False
    """
    return _request_multiple_nicks(nicks, "UPDATE notes SET hidden=0\
        WHERE nickname=:nick")


def transactions(notes, diff):
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
    rebuild_cache()
    return value


def change_ecocups(nick, diff):
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
    rebuild_cache()
    return value


def export(notes, *, csv=False, xml=False):
    """ Return an xml representation of all notes

        :param list: A list of notes to export
    """
    if xml:
        xml = "<?xml version=\"1.0\"?>\n"
        xml += "<notes date=\"{}\">\n".format(datetime.datetime.now().strftime(
            "%Y-%m-%d"))
        for note in notes:
            if note["overdraft_date"] and note["overdraft_date"].isValid():
                overdraft_date = note["overdraft_date"].toString("yyyy-MM-dd")
            else:
                overdraft_date = ""

            xml += "\t<note id=\"{}\">\n".format(note["id"])
            xml += "\t\t<prenom>{}</prenom>\n".format(note["firstname"])
            xml += "\t\t<nom>{}</nom>\n".format(note["lastname"])
            xml += "\t\t<compte>{}</compte>\n".format(note["note"])
            xml += "\t\t<mail>{}</mail>\n".format(note["mail"].split("@")[0])
            xml += "\t\t<date_Decouvert>{}</date_Decouvert>\n".format(
                overdraft_date
            )

            xml += "\t</note>\n"
        xml += "</notes>\n"
        return xml
    elif csv:
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
    return export([note for note in NOTES_CACHE if note['nickname'] in notes_nicks],
                  *args,
                  **kwargs)


rebuild_cache()

