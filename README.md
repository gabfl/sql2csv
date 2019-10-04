# sql2csv

[![Pypi](https://img.shields.io/pypi/v/sql2csv.svg)](https://pypi.org/project/sql2csv)
[![Build Status](https://travis-ci.org/gabfl/sql2csv.svg?branch=master)](https://travis-ci.org/gabfl/sql2csv)
[![codecov](https://codecov.io/gh/gabfl/sql2csv/branch/master/graph/badge.svg)](https://codecov.io/gh/gabfl/sql2csv)
[![MIT licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://raw.githubusercontent.com/gabfl/sql2csv/master/LICENSE)

Run MySQL and PostgreSQL queries and store the results in CSV.

## Why sql2csv

`sql2csv` is a small utility to run MySQL and PostgreSQL queries and store the output in a CSV file.

In some environments like when using MySQL or Aurora in AWS RDS, exporting queries' results to CSV is not available with native tools. `sql2csv` is a simple module that offers this feature.

## Installation

```bash
pip3 install sql2csv

# Basic usage
mysql [...] -e "SELECT * FROM table" | sql2csv
# or
psql [...] -c "SELECT * FROM table" | sql2csv
```

## Example

### From stdin

For simple queries you can pipe a result directly from `mysql` or `psql` to `sql2csv`.

For more complex queries, it is recommended to use the CLI (see below) to ensure a properly formatted CSV.

```bash
mysql -U root -p"secret" my_db -e "SELECT * FROM some_mysql_table;" | sql2csv

id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
```

```bash
psql -U postgres my_db -c "SELECT * FROM some_pg_table" | sql2csv

id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
```

### Using `sql2csv` CLI

#### Output to stdout

```bash
$ sql2csv --engine mysql \
  --database my_db --user root --password "secret" \
  --query "SELECT * FROM some_mysql_table"

1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
```

#### Output saved in a file

```bash
$ sql2csv --engine mysql \
  --database my_db --user root --password "secret" \
  --query "SELECT * FROM some_mysql_table" \
  --headers \
  --out file --destination_file export.csv

# * Exporting rows...
#   ...done
# * The result has been exported to export.csv.

$ cat export.csv 
id,some_int,some_str,some_date
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
```

## Usage

```bash
usage: sql2csv [-h] [-e {mysql,postgresql}] [-H HOST] [-P PORT] -u USER
               [-p PASSWORD] -d DATABASE -q QUERY [-o {stdout,file}]
               [-f DESTINATION_FILE] [-D DELIMITER] [-Q QUOTECHAR] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -e {mysql,postgresql}, --engine {mysql,postgresql}
                        Database engine
  -H HOST, --host HOST  Database host
  -P PORT, --port PORT  Database port
  -u USER, --user USER  Database user
  -p PASSWORD, --password PASSWORD
                        Database password
  -d DATABASE, --database DATABASE
                        Database name
  -q QUERY, --query QUERY
                        SQL query
  -o {stdout,file}, --out {stdout,file}
                        CSV destination
  -f DESTINATION_FILE, --destination_file DESTINATION_FILE
                        CSV destination file
  -D DELIMITER, --delimiter DELIMITER
                        CSV delimiter
  -Q QUOTECHAR, --quotechar QUOTECHAR
                        CSV quote character
  -t, --headers         Include headers
```
