#!/usr/bin/env python3

import csv
from os.path import expanduser

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


def get_cursor(connection):
    """
        Return connection cursor
    """

    return connection.cursor()


def run_query(cursor, query):
    """ Run a query and yield each row """

    cursor.execute(query)

    for row in cursor.fetchall():
        yield row


def resolve_home_dir(destination):
    """ Resolve `~` to a full path """

    if destination[:1] == '~':
        return expanduser("~") + destination[1:]

    return destination


def open_file(destination):
    """ Open file """

    return open(destination, 'w', newline='')


def get_writer(file_, delimiter=',', quotechar='"'):
    """ Return a writer object """

    return csv.writer(
        file_,
        delimiter=delimiter,
        quotechar=quotechar, quoting=csv.QUOTE_MINIMAL
    )


def to_csv(engine, host, user, port, password, database, query, destination, delimiter=',', quotechar='"'):
    """ Run a query and store the result to a CSV file """

    # Get SQL connection
    connection = get_connection(
        engine=engine,
        host=host,
        user=user,
        port=port,
        password=password,
        database=database
    )
    cursor = get_cursor(connection)

    print('\n* Exporting rows...')

    # Open CSV
    file_ = open_file(resolve_home_dir(destination))
    writer = get_writer(file_, delimiter=delimiter, quotechar=quotechar)

    # Run query and write rows to CSV
    i = 0
    for row in run_query(cursor=cursor, query=query):
        # Increment row counter
        i += 1

        if i % 100 == 0:
            print('  ...%s rows written' % "{:,}".format(i))

        writer.writerow(row)

    print('  ...done')

    print('* The result has been exported to %s.\n' % (destination))


def main():
    """ Parses arguments and run module """

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--engine", type=str, help="Database engine",
                        choices=['mysql', 'postgresql'], default='mysql')
    parser.add_argument("-H", "--host", default="127.0.0.1",
                        help="Database host")
    parser.add_argument("-P", "--port", type=int,
                        default=3306, help="Database port")
    parser.add_argument("-u", "--user", required=True, help="Database user")
    parser.add_argument("-p", "--password", default='',
                        help="Database password")
    parser.add_argument("-d", "--database", required=True,
                        help="Database name")
    parser.add_argument("-q", "--query", required=True,
                        help="SQL query")
    parser.add_argument("-o", "--out",
                        help="CSV destination", default='export.csv')
    parser.add_argument("-D", "--delimiter", help="CSV delimiter", default=',')
    parser.add_argument("-Q", "--quotechar",
                        help="CSV quote character", default='"')
    args = parser.parse_args()

    to_csv(
        engine=args.engine,
        host=args.host,
        user=args.user,
        port=args.port,
        password=args.password,
        database=args.database,
        query=args.query,
        destination=args.out,
        delimiter=args.delimiter,
        quotechar=args.quotechar
    )


if __name__ == '__main__':
    main()
