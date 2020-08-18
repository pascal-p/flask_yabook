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
ls -la . project/
echo "--------------------------------"

## Start App (already in /app)
#/bin/bash -c 'source /app/.env_staging && python src/main.py'

/bin/bash -c 'source /app/.env_staging && python manage.py run -h 0.0.0.0'
