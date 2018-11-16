# sql2csv

[![Pypi](https://img.shields.io/pypi/v/sql2csv.svg)](https://pypi.org/project/sql2csv)
[![Build Status](https://travis-ci.org/gabfl/sql2csv.svg?branch=master)](https://travis-ci.org/gabfl/sql2csv)
[![codecov](https://codecov.io/gh/gabfl/sql2csv/branch/master/graph/badge.svg)](https://codecov.io/gh/gabfl/sql2csv)
[![MIT licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://raw.githubusercontent.com/gabfl/sql2csv/master/LICENSE)

Run MySQL and PostgreSQL queries and store result in CSV

## Why sql2csv

`sql2csv` allows to export the result of MySQL and PostgreSQL queries to CSV files.

`sql2csv` helps exporting queries result from AWS RDS to CSV.

## Installation

```bash
pip3 install sql2csv
```

### Example

```bash
$ sql2csv --engine mysql \
  --database my_db --user root --password "secret" \
  --query "SELECT * FROM some_mysql_table" \
  --out export.csv

# * Exporting rows...
#   ...done
# * The result has been exported to export.csv.

$ cat export.csv 
1,12,hello world,2018-12-01 12:23:12
2,15,hello,2018-12-05 12:18:12
3,18,world,2018-12-08 12:17:12
```

### Usage

```bash
sql2csv --help
usage: sql2csv [-h] [-e {mysql,postgresql}] [-H HOST] [-P PORT] -u USER
               [-p PASSWORD] -d DATABASE -q QUERY [-o OUT] [-D DELIMITER]
               [-Q QUOTECHAR]

optional arguments:
  -h, --help            show this help message and exit
  -e {mysql,postgresql}, --engine {mysql,postgresql}
                                        Database engine
  -H HOST, --host HOST                  Database host
  -P PORT, --port PORT                  Database port
  -u USER, --user USER                  Database user
  -p PASSWORD, --password PASSWORD      Database password
  -d DATABASE, --database DATABASE      Database name
  -q QUERY, --query QUERY               SQL query
  -o OUT, --out OUT                     CSV destination
  -D DELIMITER, --delimiter DELIMITER   CSV delimiter
  -Q QUOTECHAR, --quotechar QUOTECHAR   CSV quote character
```