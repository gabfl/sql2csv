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
            db_config['host'], db_config['user'], db_config['port'], db_config['password'], db_config['db'])

        self.assertIsInstance(
            connection, psycopg2.extensions.connection)
