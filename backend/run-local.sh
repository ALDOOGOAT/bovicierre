#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")"
secret_dir="${BOVI_SECRETS_DIR:-${BOVI_SECRET_DIR:-$HOME/.local/share/bovicierre-academic/secrets}}"
for secret_name in app_a_password app_b_password auth_password worker_password; do
    if [[ ! -s "$secret_dir/$secret_name" ]]; then
        echo "Falta el secreto externo: $secret_name" >&2
        exit 1
    fi
done
export BOVI_DB_A_PASSWORD="$(cat "$secret_dir/app_a_password")"
export BOVI_DB_B_PASSWORD="$(cat "$secret_dir/app_b_password")"
export BOVI_AUTH_PASSWORD="$(cat "$secret_dir/auth_password")"
export BOVI_WORKER_PASSWORD="$(cat "$secret_dir/worker_password")"
export BOVI_DOCUMENTS_DIR="${BOVI_DOCUMENTS_DIR:-$HOME/.local/share/bovicierre-academic/private-documents}"
runtime_dir="${BOVI_RUNTIME_DIR:-$HOME/.local/share/bovicierre-academic/run}"
mkdir -p "$runtime_dir"
chmod 700 "$runtime_dir"
export BOVI_RUNTIME_DIR="$runtime_dir"
echo "API local: http://127.0.0.1:${BOVI_API_PORT:-18080}; PID y registro privados en $runtime_dir"
exec ./mvnw spring-boot:run "$@" >> "$runtime_dir/api.log" 2>&1
