import unittest
import _io

import psycopg2
import pymysql

from .. import sql2csv


class Test(unittest.TestCase):

    db_configs = {
        'mysql': {
            'engine': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'user': 'travis',
            'password': '',
            'db': 'my_db'
        },
        'pg': {
            'engine': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '',
            'db': 'my_db'
        }
    }

    def get_connection(self, engine):

        db_config = self.db_configs['pg' if engine ==
                                    'postgresql' else 'mysql']

        # Get database connection
        return sql2csv.get_connection(
            engine=engine,
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )

    def test_get_mysql_connection(self):
        db_config = self.db_configs['mysql']

        # Get database connection
        connection = sql2csv.get_mysql_connection(
            db_config['host'], db_config['user'], db_config['port'], db_config['password'], db_config['db'])

        self.assertIsInstance(connection, pymysql.connections.Connection)

    def test_get_pg_connection(self):
        db_config = self.db_configs['pg']

        # Get database connection
        connection = sql2csv.get_pg_connection(
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )

        self.assertIsInstance(connection, psycopg2.extensions.connection)

    def test_get_connection_engine_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        self.assertIsInstance(connection, pymysql.connections.Connection)

    def test_get_connection_engine_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        self.assertIsInstance(connection, psycopg2.extensions.connection)

    def test_get_connection_engine_invalid_engine(self):
        db_config = self.db_configs['pg']

        self.assertRaises(
            RuntimeError,
            sql2csv.get_connection,
            engine='invalid',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )

    def test_resolve_home_dir(self):
        assert sql2csv.resolve_home_dir('/tmp/file') == '/tmp/file'
        assert sql2csv.resolve_home_dir('~/file') == '/root/file'

    def test_open_file(self):
        self.assertIsInstance(sql2csv.open_file(
            '/tmp/file1'), _io.TextIOWrapper)

    def test_get_writer(self):
        file_ = sql2csv.open_file('/tmp/file2')
        writer = sql2csv.get_writer(file_)

        self.assertIsInstance(writer, object)

    def get_cursor_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        cursor = sql2csv.get_cursor(connection)

        self.assertIsInstance(cursor, pymysql.cursors.Cursor)

    def get_cursor_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        cursor = sql2csv.get_cursor(connection)

        self.assertIsInstance(cursor, psycopg2.extensions.cursor)

    def test_run_query_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        cursor = sql2csv.get_cursor(connection)

        for row in sql2csv.run_query(cursor=cursor, query='SELECT 1;'):
            self.assertIsInstance(row, tuple)

    def test_run_query_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        cursor = sql2csv.get_cursor(connection)

        for row in sql2csv.run_query(cursor=cursor, query='SELECT generate_series(1, 5);'):
            self.assertIsInstance(row, tuple)

    def test_to_csv_mysql(self):
        db_config = self.db_configs['mysql']

        dest_file = '/tmp/file3'

        sql2csv.to_csv(
            engine='mysql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query='SELECT * FROM some_mysql_table',
            destination=dest_file
        )

        # Read file
        with open(dest_file, 'r') as content_file:
            content = content_file.read()

        assert content == """1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
"""

    def test_to_csv_postgresql(self):
        db_config = self.db_configs['pg']

        dest_file = '/tmp/file4'

        sql2csv.to_csv(
            engine='postgresql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query='SELECT * FROM some_pg_table',
            destination=dest_file
        )

        # Read file
        with open(dest_file, 'r') as content_file:
            content = content_file.read()

        assert content == """1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
"""
