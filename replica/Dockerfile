# Dockerfile для репликации базы данных

FROM postgres:15.6-alpine

# Копируем скрипт для настройки репликации
COPY start_script.sh /var/lib/postgresql/start_script.sh
RUN chmod 0755 /var/lib/postgresql/start_script.sh


