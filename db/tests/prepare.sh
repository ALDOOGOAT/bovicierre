#!/bin/sh
# Namespace separado por pruebas; jamás DROP/reset ni reemplazo de datos.
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
for database in bovicierre_gold_final bovicierre_release_replay; do
 for node in a b prov; do
  container="bovicierre-academic-pg-$node-1"
  label=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$container")
  [ "$label" = bovicierre-academic ] || exit 1
  exists=$(docker exec "$container" psql -qAt -U postgres -d postgres -c "SELECT count(*) FROM pg_database WHERE datname='$database'")
  if [ "$exists" = 0 ]; then docker exec "$container" psql -q -U postgres -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE $database"; fi
 done
 BOVI_DB_NAME="$database" sh "$repo_dir/db/bootstrap/migrate.sh"
 BOVI_DB_NAME="$database" python3 "$repo_dir/db/bootstrap/bootstrap.py"
done
