#!/bin/sh
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
secret_dir=${BOVI_SECRET_DIR:-"$HOME/.local/share/bovicierre-academic/secrets"}
mvn -q -f "$repo_dir/db/migrate/pom.xml" package dependency:copy-dependencies
for port in "${BOVI_MIGRATION_PORT_A:-15432}" "${BOVI_MIGRATION_PORT_B:-15433}"; do
 java -cp "$repo_dir/db/migrate/target/classes:$repo_dir/db/migrate/target/dependency/*" mx.bovicierre.Migrate "jdbc:postgresql://127.0.0.1:$port/${BOVI_DB_NAME:-bovicierre}" "$secret_dir/admin_password" "$repo_dir/db/migrations"
done
