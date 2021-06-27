#!/bin/sh

rm -rf ./psql
rm -rf ./sandbox_db
pg_ctl initdb -D ./psql
pg_ctl initdb -D ./sandbox_db
pg_ctl start -D ./psql -o "-p 54321"
pg_ctl start -D ./sandbox_db -o "-p 54320"

psql -d postgres -p 54321 -f db_definitions.sql
psql -d postgres -p 54320 -f sandbox_db_definitions.sql

psql -d sqlabo -p 54321 -U web -f table_definitions.sql

pg_ctl stop -D ./psql
pg_ctl stop -D ./sandbox_db
