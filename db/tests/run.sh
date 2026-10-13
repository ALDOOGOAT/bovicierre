#!/bin/sh
# Pruebas requieren bases aisladas preparadas; nunca sustituye main ni borra datos.
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
test_env=${BOVI_TEST_VENV:-"$HOME/.cache/bovicierre/sql-tests"}
if [ ! -x "$test_env/bin/python" ]; then
 python3 -m venv "$test_env"
 "$test_env/bin/pip" -q install -r "$repo_dir/db/requirements.txt"
fi
cd "$repo_dir"
"$test_env/bin/python" db/tests/gold.py
"$test_env/bin/python" db/tests/gold_acad.py
"$test_env/bin/python" db/tests/password_reset.py
"$test_env/bin/python" db/tests/empty_install.py
"$test_env/bin/python" db/tests/academic.py
"$test_env/bin/python" db/tests/infra_evidence.py
"$test_env/bin/python" db/tests/provider.py
"$test_env/bin/python" db/tests/negatives.py
"$test_env/bin/python" db/tests/expiry.py
"$test_env/bin/python" db/tests/owner_capture.py
"$test_env/bin/python" db/tests/provider_precision.py
"$test_env/bin/python" db/tests/version_guards.py
"$test_env/bin/python" db/tests/weighing_reports.py
"$test_env/bin/python" db/tests/closure_order.py
"$test_env/bin/python" db/tests/performance.py
for node in a b; do docker exec -i "bovicierre-academic-pg-$node-1" psql -q -U postgres -d bovicierre -v ON_ERROR_STOP=1 < db/tests/security.sql; done
