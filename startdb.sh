#!/bin/sh
pg_ctl start -D ./db/psql -o "-p 54321"
pg_ctl start -D ./db/sandbox_db -o "-p 54320"
