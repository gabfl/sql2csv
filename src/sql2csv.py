#!/usr/bin/env python3

import sys
import csv
import tempfile
from os.path import expanduser

import argparse
import pymysql.cursors
import pymysql.constants.CLIENT
import psycopg2.extras
import psycopg2

file_ = None


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


def discard_line(line):
    """ Decide whether we should keep or dicard a line """

    if line[:1] in ['', '+', '(', '-']:
        return True

    return False


def remove_leading_trailing_pipe(line):
    """ Remove optional leading and trailing pipe """

    return line.strip('|')


def get_column_separator(input_):
    """ Return the column separator """
    """ This logic needs to be improved """

    if input_.count('|') > input_.count('\t'):
        return '|'

    return '\t'


def split_columns(line, separator='\t'):
    """ Split a line by pipe """

    return line.split(separator)


def strip_whitespaces(tpl):
    """ Strip white spaces before and after each item """

    return [item.strip() for item in tpl]


def has_stdin_input():
    """ Return `True` if there is an stdin input """

    if not sys.stdin.isatty():
        return True

    return False


def resolve_home_dir(destination):
    """ Resolve `~` to a full path """

    if destination[:1] == '~':
        return expanduser("~") + destination[1:]

    return destination


def open_file(destination):
    """ Open file """

    global file_

    file_ = open(destination, 'w+', newline='')

    return file_


def open_tempfile():
    """ Open a temporary file """

    global file_

    file_ = tempfile.NamedTemporaryFile('w+', newline='', delete=False)

    return file_


def get_writer(file_, delimiter=',', quotechar='"'):
    """ Return a writer object """

    return csv.writer(
        file_,
        delimiter=delimiter,
        quotechar=quotechar, quoting=csv.QUOTE_MINIMAL
    )


def file_to_stdout():
    """ Print file content to stdout """

    with open(file_.name) as f:
        print(f.read())


def stdin_to_csv(delimiter=',', quotechar='"'):
    """ Parse stdin and return output in a CSV format """

    # Open CSV
    with open_tempfile() as file_:
        writer = get_writer(file_, delimiter=delimiter, quotechar=quotechar)

        # Parse lines and add to file
        separator = None
        for line in sys.stdin:
            # Strip whitespaces
            line.strip()

            if not discard_line(line):
                # Get column separator
                separator = get_column_separator(
                    line) if not separator else separator

                # Remove leading and trailing |
                line = remove_leading_trailing_pipe(line)

                if line.strip():
                    # Split columns with separator
                    row = split_columns(line, separator)

                    # Add to CSV
                    row = strip_whitespaces(row)

                    # Write row
                    writer.writerow(row)

    file_to_stdout()


def query_to_csv(engine, host, user, port, password, database, query, out_type='stdout', destination_file=None, delimiter=',', quotechar='"', print_info=1000):
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

    if out_type == 'file':
        print('\n* Exporting rows...')

    with open_tempfile() if out_type == 'stdout' else open_file(resolve_home_dir(destination_file)) as file_:
        writer = get_writer(file_, delimiter=delimiter, quotechar=quotechar)

        # Run query and write rows to CSV
        i = 0
        for row in run_query(cursor=cursor, query=query):
            # Increment row counter
            i += 1

            if out_type == 'file' and i % print_info == 0:
                print('  ...%s rows written' % "{:,}".format(i))

            writer.writerow(row)

        if out_type == 'file':
            print('  ...done')
            print('* The result has been exported to %s.\n' %
                  (destination_file))

    # Print stdout
    if out_type == 'stdout':
        file_to_stdout()


def main():
    """ Parses arguments and run module """

    # Intercept and parse stdin input
    if has_stdin_input():
        # Parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-D", "--delimiter",
                            help="CSV delimiter", default=',')
        parser.add_argument("-Q", "--quotechar",
                            help="CSV quote character", default='"')
        args = parser.parse_args()

        return stdin_to_csv(delimiter=args.delimiter, quotechar=args.quotechar)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", type=str, help="Database engine",
                        choices=['mysql', 'postgresql'], default='mysql')
    parser.add_argument("-H", "--host", default="127.0.0.1",
                        help="Database host")
    parser.add_argument("-P", "--port", type=int,
                        help="Database port")
    parser.add_argument("-u", "--user", required=True, help="Database user")
    parser.add_argument("-p", "--password", default='',
                        help="Database password")
    parser.add_argument("-d", "--database", required=True,
                        help="Database name")
    parser.add_argument("-q", "--query", required=True,
                        help="SQL query")
    parser.add_argument("-o", "--out",
                        help="CSV destination", choices=['stdout', 'file'],
                        default='stdout')
    parser.add_argument("-f", "--destination_file",
                        help="CSV destination file")
    parser.add_argument("-D", "--delimiter", help="CSV delimiter", default=',')
    parser.add_argument("-Q", "--quotechar",
                        help="CSV quote character", default='"')
    args = parser.parse_args()

    # Set default port
    if not args.port:
        if args.engine == 'postgresql':
            args.port = 5432  # PG default
        else:
            args.port = 3306  # MySQL default

    # Force output to file if there is a file
    if args.destination_file:
        args.out = 'file'

    query_to_csv(
        engine=args.engine,
        host=args.host,
        user=args.user,
        port=args.port,
        password=args.password,
        database=args.database,
        query=args.query,
        out_type=args.out,
        destination_file=args.destination_file,
        delimiter=args.delimiter,
        quotechar=args.quotechar
    )


if __name__ == '__main__':
    main()
