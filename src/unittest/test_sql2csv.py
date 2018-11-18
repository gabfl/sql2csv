import unittest
import _io
import tempfile
import sys
from unittest.mock import patch
from io import StringIO

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

        db_config = self.db_configs[
            'pg' if engine == 'postgresql' else 'mysql'
        ]

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

    def test_discard_line(self):
        assert sql2csv.discard_line('+something') is True
        assert sql2csv.discard_line('(something') is True
        assert sql2csv.discard_line('-something') is True
        assert sql2csv.discard_line('') is True
        assert sql2csv.discard_line('something') is False

    def test_remove_leading_trailing_pipe(self):
        assert sql2csv.remove_leading_trailing_pipe(
            '|something|') == 'something'
        assert sql2csv.remove_leading_trailing_pipe('something') == 'something'

    def test_get_column_separator(self):
        assert(sql2csv.get_column_separator('some|value|is\nseparated')) == '|'
        assert(sql2csv.get_column_separator(
            'some\tvalue\tis|separated')) == '\t'

    def test_split_columns(self):
        assert sql2csv.split_columns(
            'some\tthing\telse') == ['some', 'thing', 'else']

    def test_split_columns_2(self):
        assert sql2csv.split_columns(
            'some|thing|else', separator='|') == ['some', 'thing', 'else']

    def test_strip_whitespaces(self):
        assert sql2csv.strip_whitespaces(
            ['  some  ', '  thing', 'else  ']) == ['some', 'thing', 'else']

    # def test_has_stdin_input(self):
    #     assert sql2csv.has_stdin_input() is False

    def test_has_stdin_input_2(self):
        with patch("sys.stdin", StringIO("some input")):
            assert sql2csv.has_stdin_input() is True

    def test_resolve_home_dir(self):
        assert sql2csv.resolve_home_dir('/tmp/file') == '/tmp/file'
        assert sql2csv.resolve_home_dir('~/file') == '/home/travis/file'

    def test_open_file(self):
        self.assertIsInstance(sql2csv.open_file(
            '/tmp/file1'), _io.TextIOWrapper)

    def test_open_tempfile(self):
        self.assertIsInstance(sql2csv.open_tempfile(),
                              tempfile._TemporaryFileWrapper)

    def test_get_writer(self):
        file_ = sql2csv.open_tempfile()
        writer = sql2csv.get_writer(file_)

        self.assertIsInstance(writer, object)

    def test_file_to_stdout(self):
        with tempfile.NamedTemporaryFile(mode='w+', newline='') as file_:
            # Write some dummy content
            file_.write('some line\n')
            file_.write('some other line')
            file_.flush()

            saved_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out

                # Render file content to stdout
                sql2csv.file_ = file_
                sql2csv.file_to_stdout()

                output = out.getvalue().strip()
                assert output == 'some line\nsome other line'
            finally:
                sys.stdout = saved_stdout

    def test_stdin_to_csv(self):
        with patch("sys.stdin", StringIO(""" id | some_int |  some_str   |      some_date 
----+----------+-------------+---------------------
  1 |       12 | hello world | 2018-12-01 12:23:12
  2 |       15 | hello       | 2018-12-05 12:18:12
  3 |       18 | world       | 2018-12-08 12:17:12
""")):
            saved_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out

                # Parse input and render CSV to stdout
                sql2csv.stdin_to_csv()

                output = out.getvalue().strip()
                print(output)
                assert output == """id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12"""
            finally:
                sys.stdout = saved_stdout

    def test_query_to_csv_mysql(self):
        db_config = self.db_configs['mysql']

        dest_file = '/tmp/file2'

        sql2csv.query_to_csv(
            engine='mysql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query='SELECT * FROM some_mysql_table',
            out_type='file',
            destination_file=dest_file,
            print_info=2
        )

        # Read file
        with open(dest_file, 'r') as content_file:
            content = content_file.read()

        assert content == """1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
"""

    def test_query_to_csv_postgresql(self):
        db_config = self.db_configs['pg']

        dest_file = '/tmp/file2'

        sql2csv.query_to_csv(
            engine='postgresql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query='SELECT * FROM some_pg_table',
            out_type='file',
            destination_file=dest_file
        )

        # Read file
        with open(dest_file, 'r') as content_file:
            content = content_file.read()

        assert content == """1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
"""

    def test_query_to_csv_stdout(self):
        db_config = self.db_configs['mysql']

        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out

            # Render file content to stdout
            sql2csv.query_to_csv(
                engine='mysql',
                host=db_config['host'],
                user=db_config['user'],
                port=db_config['port'],
                password=db_config['password'],
                database=db_config['db'],
                query='SELECT * FROM some_mysql_table',
                out_type='stdout',
                print_info=2
            )

            output = out.getvalue().strip()
            assert output == """1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12"""
        finally:
            sys.stdout = saved_stdout
