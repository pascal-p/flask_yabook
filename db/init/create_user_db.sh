#!/bin/sh

set -ue
umask 022

PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin"

readonly DB_TMPL="template_${DB_NAME_PREFX}"
readonly COMMON_OPTS='-v ON_ERROR_STOP=1 --username postgres'

psql ${COMMON_OPTS} <<-EOSQL
UPDATE pg_database SET datallowconn = TRUE WHERE datname = 'template0';

\c template0
DROP DATABASE IF EXISTS ${DB_TMPL};
CREATE DATABASE ${DB_TMPL} ENCODING='UTF-8' LC_CTYPE='en_NZ.utf8' LC_COLLATE='en_NZ.utf8' TEMPLATE template0;
COMMENT ON DATABASE ${DB_TMPL} IS 'default template for ${DB_NAME_PREFX} databases';
UPDATE pg_database SET datistemplate = TRUE WHERE datname = '${DB_TMPL}';

\c ${DB_TMPL}
CREATE EXTENSION IF NOT EXISTS plpgsql SCHEMA pg_catalog VERSION "1.0";
COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;
COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';

-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public;
-- COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';

VACUUM FULL FREEZE;

\c postgres
UPDATE pg_database SET datallowconn = FALSE WHERE datname = 'template0';
UPDATE pg_database SET datacl = '{=c/postgres,postgres=CTc/postgres}' WHERE datname = '${DB_TMPL}';
REVOKE CONNECT ON DATABASE postgres FROM PUBLIC;
GRANT  CONNECT ON DATABASE postgres TO   postgres;

EOSQL

psql ${COMMON_OPTS} <<-EOSQL
DROP ROLE IF EXISTS ${DB_USER};
CREATE ROLE ${DB_USER} WITH LOGIN NOSUPERUSER INHERIT CREATEROLE PASSWORD '${DB_PWD}';
ALTER USER ${DB_USER} CONNECTION LIMIT 128;
EOSQL

## Create DB instance (could be several...)
for db in ${DB_NAME_PREFX}_${DB_ENV}; do
  psql ${COMMON_OPTS} <<-EOSQL
DROP DATABASE IF EXISTS $db;
CREATE DATABASE $db WITH OWNER=${DB_USER} TEMPLATE ${DB_TMPL};
GRANT CONNECT ON DATABASE $db TO ${DB_USER};
EOSQL

  for infile in $(ls /tmp/[0-9][0-9]*.sql | sort); do
    psql -v ON_ERROR_STOP=1 -U ${DB_USER} -d $db -f $infile
  done
done

psql ${COMMON_OPTS} <<-EOSQL
ALTER DATABASE ${DB_TMPL} WITH CONNECTION LIMIT 0;
EOSQL

#
# revoke connection from all existing DBs but the ${DB_NAME_PREFX}* ones
# NOTE: remember they won't be any new DB - if new DB to create => new container
#
dbs_list=$(psql ${COMMON_OPTS} -t postgres <<-EOSQL
SELECT db.datname
FROM pg_catalog.pg_database AS db
WHERE NOT(db.datname like '${DB_NAME_PREFX}_%')
ORDER BY 1;
EOSQL
)

# Postgres already off limit
for db in $dbs_list; do
  psql ${COMMON_OPTS} <<-EOSQL
REVOKE CONNECT ON DATABASE $db FROM ${DB_USER};
EOSQL
done

echo " ==> $0 done"
