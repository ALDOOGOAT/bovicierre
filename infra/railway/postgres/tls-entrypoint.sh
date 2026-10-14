#!/bin/sh
set -eu
d=/var/lib/postgresql/certs
if [ ! -s "$d/server.key" ]; then
 mkdir -p "$d"
 openssl req -x509 -newkey rsa:2048 -nodes -days 825 -subj "/CN=bovicierre-railway" -keyout "$d/server.key" -out "$d/server.crt" 2>/dev/null
fi
chown -R postgres:postgres "$d"; chmod 700 "$d"; chmod 600 "$d/server.key"
exec docker-entrypoint.sh "$@"
