import unittest
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

    def test_get_mysql_connection(self):
        db_config = self.db_configs['mysql']

        # Get database connection
        connection = sql2csv.get_mysql_connection(
            db_config['host'], db_config['user'], db_config['port'], db_config['password'], db_config['db'])

        self.assertIsInstance(
            connection, pymysql.connections.Connection)

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

        self.assertIsInstance(
            connection, psycopg2.extensions.connection)

    def test_get_connection_engine_mysql(self):
        db_config = self.db_configs['mysql']

        # Get database connection
        connection = sql2csv.get_connection(
            engine='mysql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )

        self.assertIsInstance(
            connection, psycopg2.extensions.connection)

    def test_get_connection_engine_postgresql(self):
        db_config = self.db_configs['pg']

        # Get database connection
        connection = sql2csv.get_connection(
            engine='postgresql',
            host=db_config['host'],
            user=db_config['user'],
            port=db_config['port'],
            password=db_config['password'],
            database=db_config['db']
        )

        self.assertIsInstance(
            connection, psycopg2.extensions.connection)

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
