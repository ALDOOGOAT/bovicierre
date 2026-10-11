#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--execute" ) ]]; then
    echo "Uso: $0 [--execute]; sin argumentos sólo diagnostica." >&2
    exit 2
fi
./mvnw -q compile dependency:build-classpath -Dmdep.outputFile=target/cleanup-classpath
exec java -cp "target/classes:$(cat target/cleanup-classpath)" mx.bovicierre.evidencia.CleanupMain "$@"
