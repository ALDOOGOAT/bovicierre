#!/bin/sh
set -eu
umask 077
read_secret() {
    name="$1"
    file="$2"
    if [ -n "$file" ]; then
        [ -r "$file" ] || { echo "Archivo de secreto no disponible: $name" >&2; exit 1; }
        value=$(cat "$file")
        export "$name=$value"
        unset value
    fi
}
read_secret BOVI_DB_A_PASSWORD "${BOVI_DB_A_PASSWORD_FILE:-}"
read_secret BOVI_DB_B_PASSWORD "${BOVI_DB_B_PASSWORD_FILE:-}"
read_secret BOVI_AUTH_PASSWORD "${BOVI_AUTH_PASSWORD_FILE:-}"
read_secret BOVI_WORKER_PASSWORD "${BOVI_WORKER_PASSWORD_FILE:-}"
exec java ${JAVA_OPTS:-} -jar /app/bovicierre.jar "$@"
