import os
import sqlite3
from utils import enum

__author__ = 'Rob Derksen (boisei0)'

base_path = os.path.dirname(os.path.abspath(__file__))


class DBHandler:
    def __init__(self, dbname=os.path.join(base_path, 'data', 'autiagenda.db')):
        first_run = True
        if os.path.exists(dbname):
            first_run = False

        self._conn = sqlite3.connect(dbname)
        self._cur = self._conn.cursor()

        self._activity_type = enum('lesson', 'homework')
        self._homework_type = enum('read', 'make', 'learn', 'test-small', 'test-large', 'exam')

        if first_run:
            self._ddl()

    def _ddl(self):
        self._cur.execute('CREATE TABLE Courses \
        (id INTEGER NOT NULL, name TEXT NOT NULL UNIQUE, abbr TEXT NOT NULL, active BOOLEAN NOT NULL, \
        colour_r REAL NOT NULL, colour_g REAL NOT NULL, colour_b REAL NOT NULL, colour_a REAL NOT NULL, \
        PRIMARY KEY (id))')
        self._cur.execute('CREATE TABLE Schedule \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, time_from TEXT NOT NULL, time_to TEXT NOT NULL, \
        PRIMARY KEY (id), FOREIGN KEY (course_id) REFERENCES Courses(id))')
        self._cur.execute('CREATE TABLE Holiday \
        (id INTEGER NOT NULL, time_from INTEGER NOT NULL, time_to INTEGER NOT NULL, PRIMARY KEY (id))')
        self._cur.execute('CREATE TABLE Activity \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, homework_id INTEGER NOT NULL, activity_type INTEGER NOT NULL,\
        timestamp_from INTEGER NOT NULL, timestamp_to INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NULL, \
        notification BOOL, PRIMARY KEY (id), FOREIGN KEY (course_id) REFERENCES Courses(id), \
        FOREIGN KEY (homework_id) REFERENCES Homework(id))')
        self._cur.execute('CREATE TABLE Homework \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, homework_type INTEGER NOT NULL, description TEXT NOT NULL, \
        PRIMARY KEY (id))')
        self._conn.commit()

    def _get_homework_icon_path(self, key):
        return '{}.png'.format(os.path.join(base_path, 'res', 'homework_type', self._homework_type.reverse[key]))

    def get_no_courses(self):
        return self._cur.execute('SELECT COUNT(*) FROM Courses').fetchall()[0][0]