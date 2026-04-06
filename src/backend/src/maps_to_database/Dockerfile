FROM postgres:17-bookworm

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres_password 

RUN apt-get update &&\
apt-get install -y vim postgresql-17-postgis-3 &&\
rm -rf /var/lib/apt/lists/*

RUN mkdir -p /docker-entrypoint-initdb.d

# Script for changing the default postgres config.
# We add underscore as the prefix to the dst path because the docker-entrypoint-initdb.d/ dir executes scripts in alphabetical order:
COPY conf_database_update.sh /docker-entrypoint-initdb.d/_conf_database_update.sh
COPY postgre_sql_conf.conf /tmp/

# Script for adding postgis and other extensions.
COPY init_database.sh /docker-entrypoint-initdb.d/postgis.sh
# Helpers for seeding tiles.
COPY postgresql_helpers_function.sql /
