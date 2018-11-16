#!/usr/bin/env python3

import csv

import argparse
import pymysql.cursors
import pymysql.constants.CLIENT
import psycopg2.extras
import psycopg2


def get_mysql_connection(host, user, port, password, database, ssl={}):
    """
        MySQL connection
    """

    return pymysql.connect(host=host,
                           user=user,
                           port=port,
                           password=password,
                           db=database,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor,
                           client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
                           ssl=ssl
                           )


def get_pg_connection(host, user, port, password, database, ssl={}):
    """
        PostgreSQL connection
    """

    return psycopg2.connect(host=host,
                            user=user,
                            port=port,
                            password=password,
                            dbname=database,
                            sslmode=ssl.get('sslmode', None),
                            sslcert=ssl.get('sslcert', None),
                            sslkey=ssl.get('sslkey', None),
                            sslrootcert=ssl.get('sslrootcert', None),
                            )
