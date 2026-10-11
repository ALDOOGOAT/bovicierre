#!/bin/sh
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
export BOVI_SECRET_DIR=${BOVI_SECRET_DIR:-"$HOME/.local/share/bovicierre-academic/secrets"}
project=${BOVI_COMPOSE_PROJECT:-bovicierre-academic}
case "$project" in bovicierre-*) ;; *) printf 'Proyecto debe estar aislado bajo bovicierre-\n' >&2; exit 1 ;; esac
"$repo_dir/db/bootstrap/setup-secrets.sh"
docker compose -p "$project" -f "$repo_dir/infra/compose/compose.academic.yml" up -d --build --wait
for node in a b; do
 container="$project-pg-$node-1"
 roles=$(docker exec "$container" psql -U postgres -d "${BOVI_DB_NAME:-bovicierre}" -Atc "select count(*) from pg_roles where rolname='bovi_owner'")
 if [ "$roles" = 0 ]; then docker exec -i "$container" psql -U postgres -d "${BOVI_DB_NAME:-bovicierre}" -v ON_ERROR_STOP=1 < "$repo_dir/db/bootstrap/01_roles.sql"; fi
done
"$repo_dir/db/bootstrap/migrate.sh"
python3 "$repo_dir/db/bootstrap/bootstrap.py"
