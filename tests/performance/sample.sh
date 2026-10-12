#!/bin/sh
# Muestrea recursos cada 10 s mientras exista el archivo de control. Sólo lectura de catálogos.
# Uso: sh tests/performance/sample.sh <dir>
set -u
OUT="$1"; touch "$OUT/.sampling"
q() { docker exec bovicierre-academic-pg-a-1 psql -U postgres -d bovicierre -Atc "$1" 2>/dev/null; }
echo "ts,conexiones_a,activas_a,locks_espera_a,deadlocks_a,wal_lsn_a,xact_commit_a" > "$OUT/pg-a.csv"
while [ -f "$OUT/.sampling" ]; do
  ts=$(date -Iseconds)
  echo "$ts,$(q "select count(*), count(*) filter (where state='active'), (select count(*) from pg_locks where not granted), (select deadlocks from pg_stat_database where datname='bovicierre'), pg_current_wal_lsn(), (select xact_commit from pg_stat_database where datname='bovicierre') from pg_stat_activity where datname='bovicierre'" | tr '|' ',')" >> "$OUT/pg-a.csv"
  docker stats --no-stream --format "$ts,{{.Name}},{{.CPUPerc}},{{.MemUsage}}" $(docker ps --format '{{.Names}}' | grep '^bovicierre-academic-') >> "$OUT/docker-stats.csv"
  free -m | awk -v ts="$ts" '/^Mem:/ {print ts","$2","$3","$7}' >> "$OUT/host-mem.csv"
  sleep 10
done
