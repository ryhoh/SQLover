#!/bin/sh

rm -rf ./psql
rm -rf ./sandbox_db
pg_ctl initdb -D ./psql
pg_ctl initdb -D ./sandbox_db
pg_ctl -o "-F -p 54321" start -D ./psql
pg_ctl -o "-F -p 54320" start -D ./sandbox_db

psql -p 54321 -d postgres -f db_definitions_psql.sql
psql -p 54320 -d postgres -f db_definitions_sandbox.sql

# ここは毎回変更が必要
psql -p 54321 -d sqlovers -U web -f table_definitions.sql
# psql -p 54321 -d sqlovers -U web -f secret_definitions.sql

pg_ctl stop -D ./psql
pg_ctl stop -D ./sandbox_db
