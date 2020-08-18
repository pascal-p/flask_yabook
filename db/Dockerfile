## for APP Container

FROM postgres:12.4-alpine

## adjust shell scripts inside container
COPY ./init/create_user_db.sh /docker-entrypoint-initdb.d/

COPY ./sql/*.sql /tmp/

RUN chmod 0555 /docker-entrypoint-initdb.d/*.sh; \
  chmod 0444 /tmp/*.sql

## adjust structure.sql script in container
# RUN sed -i'' -e 's|\(^COMMENT ON EXTENSION..*\)|-- \1|g' /tmp/01_structure.sql
