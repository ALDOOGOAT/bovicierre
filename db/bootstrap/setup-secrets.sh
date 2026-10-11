#!/bin/sh
set -eu
secret_dir=${BOVI_SECRET_DIR:-"$HOME/.local/share/bovicierre-academic/secrets"}
mkdir -p "$secret_dir"
chmod 700 "$secret_dir"
umask 077
for name in admin_password app_a_password app_b_password repl_password fdw_password demo_password auth_password worker_password; do
 if [ ! -f "$secret_dir/$name" ]; then openssl rand -hex 24 > "$secret_dir/$name"; fi
done
printf 'export BOVI_SECRET_DIR=%s\n' "$secret_dir"
for name in demo_operador_password demo_caja_password demo_auditor_password; do
 if [ ! -f "$secret_dir/$name" ]; then openssl rand -hex 16 > "$secret_dir/$name"; fi
done
