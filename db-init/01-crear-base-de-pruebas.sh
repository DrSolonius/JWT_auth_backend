#!/bin/sh
# db-init/01-crear-base-de-pruebas.sh
# PostgreSQL ejecuta este script UNA sola vez, cuando el volumen pgdata esta vacio.
# Crea la segunda base (clase_test) dentro del mismo servidor que ya usa la app.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${DB_NAME_TEST:-clase_test};
EOSQL
