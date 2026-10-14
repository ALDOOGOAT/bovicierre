#!/bin/sh
set -eu
umask 077; : > /tmp/pool_passwd
# Secretos: archivo de Docker (/run/secrets/<nombre>) o, en plataformas sin archivos (Railway), variable <NOMBRE>.
secret() {
 if [ -r "/run/secrets/$1" ]; then cat "/run/secrets/$1"; else
  var=$(printf %s "$1" | tr 'a-z' 'A-Z'); eval "value=\${$var:-}"; [ -n "$value" ] || { echo "Falta secreto $1" >&2; exit 1; }; printf %s "$value"; fi
}
for pair in 'bovi_app_a:app_a_password' 'bovi_app_b:app_b_password' 'bovi_repl:repl_password' 'bovi_worker:worker_password'; do
 role=${pair%%:*}; name=${pair#*:}
 printf '%s:TEXT%s\n' "$role" "$(secret "$name")" >> /tmp/pool_passwd
done
chmod 600 /tmp/pool_passwd
conf=/etc/pgpool2/pgpool.conf
if [ -n "${BOVI_PGPOOL_BACKEND:-}" ]; then  # sin montaje de configuración: plantilla con el nodo indicado
 sed "s/^backend_hostname0 = .*/backend_hostname0 = '${BOVI_PGPOOL_BACKEND}'/" /etc/pgpool2/pgpool-template.conf > /tmp/pgpool.conf; conf=/tmp/pgpool.conf
fi
exec pgpool -n -f "$conf" -a /etc/pgpool2/pool_hba.conf
