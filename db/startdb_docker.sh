#!/bin/sh

# 2: start postgres

docker run --rm -detach \
    --publish 54321:5432 \
    --env POSTGRES_HOST_AUTH_METHOD=trust \
    --env PGDATA=/var/lib/postgresql/data/psql \
    --volume /tmp/sqlpuzzlers_db/data:/var/lib/postgresql/data \
    --name sqlpuzzlers_postgres \
    postgres:12-alpine

docker run --rm -detach \
    --publish 54320:5432 \
    --env POSTGRES_HOST_AUTH_METHOD=trust \
    --env PGDATA=/var/lib/postgresql/data/psql \
    --volume /tmp/sandbox_db/data:/var/lib/postgresql/data \
    --name sandbox_postgres \
    postgres:12-alpine
