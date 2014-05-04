import os
import sqlite3

__author__ = 'Rob Derksen (boisei0)'

base_path = os.path.dirname(__file__)


class DBHandler:
    def __init__(self, dbname=os.path.join(base_path, 'data', 'autiagenda.db')):
        first_run = True
        if os.path.exists(dbname):
            first_run = False

        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

        if first_run:
            self._ddl()

    def _ddl(self):
        self.cur.execute('CREATE TABLE Courses \
        (id INTEGER NOT NULL, name TEXT NOT NULL, abbr TEXT NOT NULL, active BOOLEAN NOT NULL, colour_r REAL NOT NULL, \
        colour_g REAL NOT NULL, colour_b REAL NOT NULL, colour_a REAL NOT NULL, PRIMARY KEY id')
        self.cur.execute('CREATE TABLE Schedule \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, time_from TEXT NOT NULL, time_to TEXT NOT NULL, \
        PRIMARY KEY id, FOREIGN KEY (course_id) REFERENCES Courses(id))')
        self.cur.execute('CREATE TABLE Activity \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, homework_id INTEGER NOT NULL, activity_type INTEGER NOT NULL,\
        timestamp_from INTEGER NOT NULL, timestamp_to INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NULL, \
        notification BOOL, PRIMARY KEY id, FOREIGN KEY (courses_id) REFERENCES Courses(id), \
        FOREIGN KEY (homework_id) REFERENCES Homework(id))')
        self.cur.execute('CREATE TABLE Homework \
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, )')
        self.conn.commit()

    # activity type can be:
    #   0   'lesson'
    #   1   'homework'