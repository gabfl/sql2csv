#!/usr/bin/env python3

import csv

import argparse
import pymysql.cursors
import pymysql.constants.CLIENT
import psycopg2.extras
import psycopg2


def get_mysql_connection(host, user, port, password, database):
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
                           client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
                           )


def get_pg_connection(host, user, port, password, database):
    """
        PostgreSQL connection
    """

    return psycopg2.connect(host=host,
                            user=user,
                            port=port,
                            password=password,
                            dbname=database
                            )


def get_connection(engine, host, user, port, password, database):
    """
        Get SQL connection
    """

    if engine == 'mysql':
        return get_mysql_connection(host, user, port, password, database)
    elif engine == 'postgresql':
        return get_pg_connection(host, user, port, password, database)
    else:
        raise RuntimeError(
            '"%s" engine is not supported.' % (engine))
