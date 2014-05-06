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
            print(ini)
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

            print(name, abbr, colour_r, colour_g, colour_b, colour_a, active, course_id)

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


if __name__ == '__main__':
    DBHandler().courses_ini_to_db()