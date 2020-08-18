#!/bin/sh

umask 022
export PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

## Need to wait...
sleep 3.1

while ! nc -zv book-db 5432; do
  sleep 0.5
done

echo "PostgreSQL started..."
echo "--------------------------------"
ls -la . src/
echo "--------------------------------"

## Start App (already in /app)
/bin/bash -c 'source /app/.env_staging && python src/main.py'

## Alt:
# /bin/bash -c 'source /app/.env_staging && python -m flask run -h 0.0.0.0'
##  --eager-loading => FLASK_DEBUG=0
