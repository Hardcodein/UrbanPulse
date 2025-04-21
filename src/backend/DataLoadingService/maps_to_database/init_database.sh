#!/bin/bash
# Инициалиция базы данных и внедрение PostGis
set -e

psql -U "$POSTGRES_USER"  -c "CREATE DATABASE maps_to_database"

psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION IF NOT EXISTS postgis"
psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION IF NOT EXISTS postgis_topology"
psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch"
psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder"
psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION postgis_sfcgal"

psql -U "$POSTGRES_USER" -d maps_to_database -c "CREATE EXTENSION IF NOT EXISTS hstore"

psql -U "$POSTGRES_USER" -d maps_to_database -a -f postgresql_helpers_function.sql