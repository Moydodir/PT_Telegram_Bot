#!/bin/bash

psql -U "$POSTGRES_USER" -d $POSTGRES_DB -c \
"
CREATE USER $USERNAME_BD_REPL REPLICATION LOGIN ENCRYPTED PASSWORD '$PASSWORD_REPL';
SELECT * FROM pg_create_physical_replication_slot('replication_slot');

CREATE TABLE IF NOT EXISTS mail_address(
    id SERIAL PRIMARY KEY,
    mail VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS phone_numbres(
    id SERIAL PRIMARY KEY,
    phone VARCHAR(500)
);
"
