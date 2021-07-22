#!/bin/sh
pg_ctl start -D ./psql -o "-p 54321"
pg_ctl start -D ./sandbox_db -o "-p 54320"
