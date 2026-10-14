#!/bin/sh
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
secret_dir=${BOVI_SECRET_DIR:-"$HOME/.local/share/bovicierre-academic/secrets"}
mvn -q -f "$repo_dir/db/migrate/pom.xml" package dependency:copy-dependencies
# Remoto (p. ej. Railway): BOVI_MIGRATION_TARGETS="host:puerto host:puerto" (A y B); por defecto el stack local.
targets=${BOVI_MIGRATION_TARGETS:-"127.0.0.1:${BOVI_MIGRATION_PORT_A:-15432} 127.0.0.1:${BOVI_MIGRATION_PORT_B:-15433}"}
for target in $targets; do
 java -cp "$repo_dir/db/migrate/target/classes:$repo_dir/db/migrate/target/dependency/*" mx.bovicierre.Migrate "jdbc:postgresql://$target/${BOVI_DB_NAME:-bovicierre}${BOVI_MIGRATION_JDBC_PARAMS:-}" "$secret_dir/admin_password" "$repo_dir/db/migrations"
done
