#!/bin/sh
set -eu
# Plataformas que montan volúmenes propiedad de root (Railway con RAILWAY_RUN_UID=0): sólo se ajusta el dueño del
# directorio de documentos y se baja a 1000:1000 sin capacidades antes de leer secretos o arrancar Java.
if [ "$(id -u)" = 0 ]; then
    chown 1000:1000 "${BOVI_DOCUMENTS_DIR:-/app/private-documents}" /app/run
    exec setpriv --reuid=1000 --regid=1000 --clear-groups --inh-caps=-all --bounding-set=-all "$0" "$@"
fi
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
