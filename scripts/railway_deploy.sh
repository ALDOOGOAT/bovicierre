#!/bin/sh
# Despliegue académico en Railway (idempotente). Requiere plan Hobby, `railway login` y el proyecto creado.
# Fases: infra (servicios, variables, volúmenes, PostgreSQL) → db (roles, migraciones, bootstrap, DEMO, cuentas)
#        → app (Pgpool, backend, frontend, Caddy y dominio). Los secretos se leen por stdin: nunca en argv ni en logs.
#   BOVI_RAILWAY_PROJECT, BOVI_RAILWAY_ENV           IDs de proyecto y entorno
#   BOVI_RAILWAY_SECRETS (def. ~/.local/share/bovicierre-academic/railway/secrets)
#   BOVI_PG_TARGETS='{"a":"host:puerto","b":…,"prov":…}' proxies TCP (fase db)
set -eu
repo=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd); cd "$repo"
P=${BOVI_RAILWAY_PROJECT:?}; E=${BOVI_RAILWAY_ENV:?}
S=${BOVI_RAILWAY_SECRETS:-$HOME/.local/share/bovicierre-academic/railway/secrets}
I=.railway.internal
export RAILWAY_CALLER=${RAILWAY_CALLER:-scripts/railway_deploy.sh}
var() { railway variable set -p "$P" -e "$E" --service "$1" --skip-deploys "$2" >/dev/null; }
sec() { railway variable set -p "$P" -e "$E" --service "$1" --skip-deploys --stdin "$2" < "$S/$3" >/dev/null; }
up() { railway up "$2" ${3:-} -p "$P" -e "$E" --service "$1" --detach -m "bovicierre $(git rev-parse --short HEAD)"; }

case "${1:?infra|db|app}" in
infra)
  have=$(railway status --json | python3 -c 'import json,sys; print("\n".join(e["node"]["name"] for e in json.load(sys.stdin)["services"]["edges"]))')
  for s in pg-a pg-b pg-prov pgpool-a pgpool-b backend frontend caddy; do
    printf '%s\n' "$have" | grep -qx "$s" || railway add -p "$P" --service "$s" --json >/dev/null
  done
  vols=$(railway volume list -p "$P" -e "$E" --json 2>/dev/null || echo '[]')
  for s in pg-a pg-b pg-prov; do
    sec "$s" POSTGRES_PASSWORD admin_password; var "$s" POSTGRES_DB=bovicierre
    printf '%s' "$vols" | grep -q "\"$s\"" || railway volume add -p "$P" -e "$E" -s "$s" -m /var/lib/postgresql --json >/dev/null
    up "$s" infra/railway/postgres --path-as-root
  done ;;
db)
  T=${BOVI_PG_TARGETS:?}
  a=$(printf '%s' "$T" | python3 -c 'import json,sys;print(json.load(sys.stdin)["a"])'); b=$(printf '%s' "$T" | python3 -c 'import json,sys;print(json.load(sys.stdin)["b"])')
  for t in "$a" "$b"; do
    PGPASSWORD=$(cat "$S/admin_password") PGSSLMODE=require psql -X -q -h "${t%:*}" -p "${t##*:}" -U postgres -d bovicierre -v ON_ERROR_STOP=1 -f db/bootstrap/01_roles.sql
  done
  BOVI_SECRET_DIR="$S" BOVI_MIGRATION_TARGETS="$a $b" BOVI_MIGRATION_JDBC_PARAMS='?sslmode=require' sh db/bootstrap/migrate.sh
  BOVI_SECRET_DIR="$S" BOVI_PSQL_TARGETS="$T" BOVI_INTERNAL_SUFFIX="$I" python3 db/bootstrap/bootstrap.py
  BOVI_SECRETS_PY=${BOVI_SECRETS_PY:-$HOME/.cache/bovicierre/sql-tests/bin/python}
  BOVI_SECRET_DIR="$S" BOVI_DEMO_TARGET="$a" "$BOVI_SECRETS_PY" db/seed/demo.py
  BOVI_SECRET_DIR="$S" BOVI_PG_TARGETS="$T" BOVI_ENTREGA_DIR="$S/../entrega" BOVI_PUBLIC_URL="${BOVI_PUBLIC_URL:-}" "$BOVI_SECRETS_PY" scripts/academic_users.py ;;
app)
  for n in a b; do
    var "pgpool-$n" "BOVI_PGPOOL_BACKEND=pg-$n$I"
    sec "pgpool-$n" APP_A_PASSWORD app_a_password; sec "pgpool-$n" APP_B_PASSWORD app_b_password
    sec "pgpool-$n" REPL_PASSWORD repl_password; sec "pgpool-$n" WORKER_PASSWORD worker_password
    up "pgpool-$n" infra/pgpool --path-as-root
  done
  var backend "BOVI_DB_A_URL=jdbc:postgresql://pgpool-a$I:9999/bovicierre"; var backend "BOVI_DB_B_URL=jdbc:postgresql://pgpool-b$I:9999/bovicierre"
  var backend "BOVI_AUTH_URL=jdbc:postgresql://pg-a$I:5432/bovicierre?sslmode=require"; var backend "BOVI_BIND_ADDRESS=::"; var backend BOVI_COOKIE_SECURE=true
  var backend "JAVA_OPTS=-Xmx384m -XX:+UseSerialGC"; var backend RAILWAY_DOCKERFILE_PATH=backend/Dockerfile; var backend RAILWAY_RUN_UID=0  # el entrypoint baja a 1000 sin capacidades tras ajustar el volumen
  sec backend BOVI_DB_A_PASSWORD app_a_password; sec backend BOVI_DB_B_PASSWORD app_b_password
  sec backend BOVI_AUTH_PASSWORD auth_password; sec backend BOVI_WORKER_PASSWORD worker_password
  vols=$(railway volume list -p "$P" -e "$E" --json 2>/dev/null || echo '[]')
  printf '%s' "$vols" | grep -q '"backend"' || railway volume add -p "$P" -e "$E" -s backend -m /app/private-documents --json >/dev/null
  up backend .
  up frontend frontend --path-as-root
  var caddy "BOVI_API_UPSTREAM=backend$I:18080"; var caddy "BOVI_WEB_UPSTREAM=frontend$I:8080"; var caddy RAILWAY_DOCKERFILE_PATH=Dockerfile.railway
  up caddy infra/caddy --path-as-root
  railway domain -p "$P" -e "$E" --service caddy --port 8080 --json || true ;;
esac
