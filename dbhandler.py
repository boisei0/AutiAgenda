import kivy
kivy.require('1.8.0')

import datetime
import os
import sqlite3

from utils import enum, unix_time

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
        (id INTEGER NOT NULL, course_id INTEGER NOT NULL, homework_id INTEGER NULL, activity_type INTEGER NOT NULL,\
        timestamp_from INTEGER NOT NULL, timestamp_to INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NULL, \
        notification BOOL, PRIMARY KEY (id), FOREIGN KEY (course_id) REFERENCES Courses(id), \
        FOREIGN KEY (homework_id) REFERENCES Homework(id))')
        self._cur.execute('CREATE TABLE Homework \
        (id INTEGER NOT NULL, homework_type INTEGER NOT NULL, description TEXT NOT NULL, \
        PRIMARY KEY (id))')
        self._conn.commit()

    def _get_homework_icon_path(self, key):
        return '{}.png'.format(os.path.join(base_path, 'res', 'homework_type', self._homework_type.reverse[key]))

    def get_no_courses(self):
        return self._cur.execute('SELECT COUNT(*) FROM Courses').fetchall()[0][0]

    def create_courses_ini_from_db(self):
        no_courses = self.get_no_courses()
        if no_courses == 0:
            # return default ini format
            ini = self._get_default_courses_ini(0)
        else:
            ini = ''
            for i in range(no_courses):
                query = 'SELECT name, abbr, active, colour_r, colour_g, colour_b, colour_a FROM Courses WHERE id=?'
                res = self._cur.execute(query, (i,)).fetchall()[0]
                ini += '[course{}]\nname = {}\nabbr = {}\n'.format(i, res[0], res[1])
                ini += 'color = [{}, {}, {}, {}]\nactive = {}\n\n'.format(res[2], res[3], res[4], res[5], res[6])

        with open(os.path.join(base_path, 'config', 'courses.ini'), 'w') as ini_file:
            ini_file.write(ini)

    @staticmethod
    def _get_default_courses_ini(course_no):
        return '[course{}]\nname = \nabbr = \ncolor = [1.0, 1.0, 1.0, 1.0]\nactive = 0\n\n'.format(course_no)

    def courses_ini_to_db(self):
        block_size = 6
        with open(os.path.join(base_path, 'config', 'courses.ini'), 'r') as ini_file:
            lines = ini_file.readlines()
        courses = len(lines) / block_size
        for i in range(courses):
            block_lines = lines[i * block_size:(i + 1) * block_size]
            start = block_lines[0].find('[course') + len('[course')
            end = block_lines[0].find(']', start)
            course_id = block_lines[0][start:end]
            name = block_lines[1][block_lines[1].find('name = ') + len('name = '):].strip()
            abbr = block_lines[2][block_lines[2].find('abbr = ') + len('abbr = '):].strip()
            start = block_lines[3].find('color = [') + len('color = [')
            end = block_lines[3].find(',', start)
            colour_r = block_lines[3][start:end]
            start = end + 2
            end = block_lines[3].find(',', start)
            colour_g = block_lines[3][start:end]
            start = end + 2
            end = block_lines[3].find(',', start)
            colour_b = block_lines[3][start:end]
            start = end + 2
            end = block_lines[3].find(']', start)
            colour_a = block_lines[3][start:end]
            active = block_lines[4][block_lines[4].find('active = ') + len('active = '):].strip()

            if self._check_course_exists(course_id):
                query = 'UPDATE Courses SET name=?, abbr=?, colour_r=?, colour_g=?, colour_b=?, colour_a=?, \
                active=? WHERE id=?'
            else:
                query = 'INSERT INTO Courses (name, abbr, colour_r, colour_g, colour_b, colour_a, active, id) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            self._cur.execute(query, (name, abbr, colour_r, colour_g, colour_b, colour_a, active, course_id,))
        self._conn.commit()

    def _check_course_exists(self, course_id):
        try:
            return len(self._cur.execute('SELECT id FROM Courses WHERE id=?', (course_id,)).fetchall()[0]) == 1
        except IndexError:
            return False

    def get_activity_data(self, activity_id):
        query = 'SELECT course_id, homework_id, activity_type, timestamp_from, timestamp_to, title, description, notification FROM Activity WHERE id=?'
        res = self._cur.execute(query, (activity_id,)).fetchall()[0]
        data = {'course_id': res[0], 'homework_id': res[1], 'activity_type': res[2], 'timestamp_from': res[3],
                'timestamp_to': res[4], 'title': res[5], 'description': res[6], 'notification': res[7]}
        return data

    def get_course_data(self, course_id):
        query = 'SELECT name, abbr, active, colour_r, colour_g, colour_b, colour_a FROM Courses WHERE id=?'
        res = self._cur.execute(query, (course_id,)).fetchall()[0]
        data = {'name': res[0], 'abbr': res[1], 'active': res[2], 'colour_r': res[3], 'colour_g': res[4],
                'colour_b': res[5], 'colour_a': res[6]}
        return data

    def get_homework_data(self, homework_id):
        query = 'SELECT homework_type, description FROM Homework WHERE id=?'
        res = self._cur.execute(query, (homework_id,)).fetchall()[0]
        data = {'homework_type': res[0], 'description': res[1]}
        return data

    def get_activity_id_by_timestamp(self, timestamp):
        if isinstance(timestamp, int):
            timestamp = datetime.datetime.utcfromtimestamp(timestamp)
        sse = unix_time(timestamp)
        query = 'SELECT id FROM Activity WHERE ? >= timestamp_from AND ? < timestamp_to'
        return self._cur.execute(query, (sse, sse,)).fetchall()[0][0]  # FIXME: Potential crash...


class ActivityModel:
    def __init__(self, activity_id):
        dbh = DBHandler()
        data = dbh.get_activity_data(activity_id)
        self.course = CourseModel(data['course_id'])
        if data['homework_id'] is not None:
            self.homework = HomeworkModel(data['homework_id'])
        else:
            self.homework = None
        self.activity_type = data['activity_type']
        self.timestamp_from = datetime.datetime.utcfromtimestamp(data['timestamp_from'])
        self.timestamp_to = datetime.datetime.utcfromtimestamp(data['timestamp_to'])
        self.title = data['title']
        self.description = data['description']
        self.notification = data['notification']


class CourseModel:
    def __init__(self, course_id):
        dbh = DBHandler()
        data = dbh.get_course_data(course_id)
        self.name = data['name']
        self.abbr = data['abbr']
        self.active = data['active']
        self.colour = [data['colour_r'], data['colour_g'], data['colour_b'], data['colour_a']]


class HomeworkModel:
    def __init__(self, homework_id):
        dbh = DBHandler()
        data = dbh.get_homework_data(homework_id)
        self.homework_type = data['homework_type']
        self.description = data['description']


if __name__ == '__main__':
    DBHandler().courses_ini_to_db()