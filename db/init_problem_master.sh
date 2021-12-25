#!/bin/sh

rm -rf ./problem_master
pg_ctl initdb -D ./problem_master
pg_ctl -o "-F -p 54322" start -D ./problem_master

psql -p 54322 -d postgres -f problem_master_db.sql
psql -p 54322 -d problem -U problem -f problem_master_table.sql

pg_ctl stop -D ./problem_master
