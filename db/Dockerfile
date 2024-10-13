# Dockerfile для основной базы данных

FROM postgres:15.6-alpine

EXPOSE 5432
RUN mkdir -p /var/lib/postgresql/WAL/archive
RUN chown postgres:postgres -R /var/lib/postgresql/WAL/archive
RUN mkdir -p /var/lib/postgressql/data && chown postgres:postgres -R /var/lib/postgressql/data
RUN mkdir -p /log/replication/ && chown postgres:postgres -R /log
USER postgres
