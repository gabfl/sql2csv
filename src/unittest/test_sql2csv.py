import unittest
import _io
import os
import tempfile
import sys
from os.path import expanduser
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
            'user': 'root',
            'password': 'root',
            'db': 'my_db'
        },
        'pg': {
            'engine': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'user': 'db_user',
            'password': 'db_password',
            'db': 'my_db'
        }
    }

    def get_connection(self, engine):

        db_config = self.db_configs[
            'pg' if engine == 'postgresql' else 'mysql'
        ]

        # Get database connection
        connection = sql2csv.get_connection(
            engine=engine,
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )
        self.addCleanup(connection.close)

        return connection

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.tmp_dir = tmp_dir.name

    def test_get_mysql_connection(self):
        db_config = self.db_configs['mysql']

        # Get database connection
        connection = sql2csv.get_mysql_connection(
            db_config['host'], db_config['user'], db_config['port'], db_config['password'], db_config['db'])
        self.addCleanup(connection.close)

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
        self.addCleanup(connection.close)

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

    def test_get_cursor_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        cursor = sql2csv.get_cursor(connection)

        self.assertIsInstance(cursor, pymysql.cursors.Cursor)

    def test_get_cursor_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        cursor = sql2csv.get_cursor(connection)

        self.assertIsInstance(cursor, psycopg2.extensions.cursor)

    def test_execute_query_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        cursor = sql2csv.get_cursor(connection)
        sql2csv.execute_query(cursor=cursor, query='SELECT 1;')

        for row in sql2csv.fetch_rows(cursor=cursor):
            self.assertIsInstance(row, tuple)

    def test_execute_query_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        cursor = sql2csv.get_cursor(connection)
        sql2csv.execute_query(
            cursor=cursor, query='SELECT generate_series(1, 5);')

        for row in sql2csv.fetch_rows(cursor=cursor):
            self.assertIsInstance(row, tuple)

    def test_fetch_headers_mysql(self):
        # Get database connection
        connection = self.get_connection(
            engine='mysql'
        )

        cursor = sql2csv.get_cursor(connection)
        sql2csv.execute_query(
            cursor=cursor, query='SELECT 1 as column1, 2 as column2;')

        assert sql2csv.fetch_headers(cursor=cursor) == ['column1', 'column2']

    def test_fetch_headers_postgresql(self):
        # Get database connection
        connection = self.get_connection(
            engine='postgresql'
        )

        cursor = sql2csv.get_cursor(connection)
        sql2csv.execute_query(
            cursor=cursor, query='SELECT 1 as column1, 2 as column2;')

        assert sql2csv.fetch_headers(cursor=cursor) == ['column1', 'column2']

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
        assert (sql2csv.get_column_separator('some|value|is\nseparated')) == '|'
        assert (sql2csv.get_column_separator(
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

    def test_stringify_items(self):
        # No change expected
        assert sql2csv.stringify_items(
            (1, 2, 'a', 'b', 'c')) == (1, 2, 'a', 'b', 'c')

        # Json encoding of dict is expected
        assert sql2csv.stringify_items((1, 2, {'a': True, 'b': False, 'c': 'some string'})) == (
            1, 2, '{"a": true, "b": false, "c": "some string"}')

    @patch('sys.stdin.isatty')
    def test_has_stdin_input(self, mocked):
        mocked.return_value = True

        assert sql2csv.has_stdin_input() is False

    def test_has_stdin_input_2(self):
        with patch("sys.stdin", StringIO("some input")):
            assert sql2csv.has_stdin_input() is True

    def test_resolve_home_dir(self):
        assert sql2csv.resolve_home_dir('/tmp/file') == '/tmp/file'
        assert sql2csv.resolve_home_dir('~/file') == expanduser('~') + '/file'

    def test_open_file(self):
        with sql2csv.open_file(os.path.join(self.tmp_dir, 'file1')) as file_:
            self.assertIsInstance(file_, _io.TextIOWrapper)

    def test_open_tempfile(self):
        with sql2csv.open_tempfile() as file_:
            self.addCleanup(os.remove, file_.name)
            self.assertIsInstance(file_, tempfile._TemporaryFileWrapper)

    def test_get_writer(self):
        with sql2csv.open_tempfile() as file_:
            self.addCleanup(os.remove, file_.name)
            writer = sql2csv.get_writer(file_, delimiter=';')
            writer.writerow(['a', 'b;c'])
            file_.flush()

            with open(file_.name) as f:
                assert f.read() == 'a;"b;c"\n'

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
                assert output == """id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12"""
            finally:
                sys.stdout = saved_stdout

    def test_query_to_csv_mysql(self):
        db_config = self.db_configs['mysql']

        dest_file = os.path.join(self.tmp_dir, 'file2.csv')

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

    def test_query_to_csv_mysql_headers(self):
        db_config = self.db_configs['mysql']

        dest_file = os.path.join(self.tmp_dir, 'file2.csv')

        sql2csv.query_to_csv(
            engine='mysql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query='SELECT * FROM some_mysql_table',
            headers=True,
            out_type='file',
            destination_file=dest_file,
            print_info=2
        )

        # Read file
        with open(dest_file, 'r') as content_file:
            content = content_file.read()

        assert content == """id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
"""

    def test_query_to_csv_postgresql(self):
        db_config = self.db_configs['pg']

        dest_file = os.path.join(self.tmp_dir, 'file2.csv')

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

    def test_file_to_stdout_remove(self):
        path = os.path.join(self.tmp_dir, 'file3')
        with open(path, 'w') as f:
            f.write('some line')

        with patch('sys.stdout', new_callable=StringIO) as out:
            with open(path) as file_:
                sql2csv.file_ = file_
                sql2csv.file_to_stdout(remove=True)

        assert out.getvalue().strip() == 'some line'
        assert not os.path.exists(path)

    def test_main_stdin(self):
        with patch('sys.stdin', StringIO("a\tb\n1\t2\n")), \
                patch('sys.argv', ['sql2csv', '-D', ';']), \
                patch('sys.stdout', new_callable=StringIO) as out:
            sql2csv.main()

        assert out.getvalue().strip() == 'a;b\n1;2'

    @patch.object(sql2csv, 'has_stdin_input', return_value=False)
    @patch.object(sql2csv, 'query_to_csv')
    def test_main_args_mysql(self, mocked_query_to_csv, mocked_stdin):
        with patch('sys.argv', ['sql2csv', '-u', 'root', '-d', 'my_db',
                                '-q', 'SELECT 1']):
            sql2csv.main()

        mocked_query_to_csv.assert_called_once_with(
            engine='mysql', host='127.0.0.1', user='root', port=3306,
            password='', database='my_db', query='SELECT 1', headers=False,
            out_type='stdout', destination_file=None, delimiter=',',
            quotechar='"'
        )

    @patch.object(sql2csv, 'has_stdin_input', return_value=False)
    @patch.object(sql2csv, 'query_to_csv')
    def test_main_args_postgresql_file(self, mocked_query_to_csv, mocked_stdin):
        with patch('sys.argv', ['sql2csv', '-e', 'postgresql', '-u', 'db_user',
                                '-d', 'my_db', '-q', 'SELECT 1', '-t',
                                '-f', 'out.csv']):
            sql2csv.main()

        kwargs = mocked_query_to_csv.call_args.kwargs
        assert kwargs['engine'] == 'postgresql'
        assert kwargs['port'] == 5432
        assert kwargs['headers'] is True
        assert kwargs['out_type'] == 'file'
        assert kwargs['destination_file'] == 'out.csv'

    def test_query_to_csv_postgresql_json(self):
        db_config = self.db_configs['pg']
        dest_file = os.path.join(self.tmp_dir, 'file4.csv')

        sql2csv.query_to_csv(
            engine='postgresql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db'],
            query="""SELECT 1 AS id, '{"a": 1}'::jsonb AS data""",
            headers=True,
            out_type='file',
            destination_file=dest_file
        )

        with open(dest_file, 'r', newline='') as content_file:
            assert content_file.read() == 'id,data\r\n1,"{""a"": 1}"\r\n'
