#!/bin/sh

# 3: (optional) setup database settings & data

psql -h 127.0.0.1 -p 54321 -d postgres -U postgres -f db_definitions_psql.sql
psql -h 127.0.0.1 -p 54320 -d postgres -U postgres -f db_definitions_sandbox.sql

psql -h 127.0.0.1 -p 54321 -d sqlpuzzlers -U web -f table_definitions.sql
