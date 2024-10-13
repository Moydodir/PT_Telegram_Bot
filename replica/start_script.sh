rm -rf /var/lib/postgresql/data/*
until pg_basebackup --pgdata=/var/lib/postgresql/data -R --slot=replication_slot --host=db --port=$PGPORT -U $POSTGRES_USER <<EOF
$POSTGRES_PASSWORD
EOF
do
sleep 2s
echo 'Waiting for primary to connect...'
sleep 1s
done
echo 'Backup done, starting replica...'

chmod 0700 /var/lib/postgresql/data
postgres
