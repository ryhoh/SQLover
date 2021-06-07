#!/bin/sh
pg_ctl stop -D ./db -o "-p 54321"
pg_ctl stop -D ./sandbox_db -o "-p 54320"
