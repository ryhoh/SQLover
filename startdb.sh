#!/bin/sh
pg_ctl start -D ./db -o "-p 54321"
pg_ctl start -D ./sandbox_db -o "-p 54320"
