.PHONY: doctor academic dev demo verify verify-docs verify-api verify-sql verify-release-local setup-tools backup restore-check stop

BOVI_SECRET_DIR ?= $(HOME)/.local/share/bovicierre-academic/secrets
export BOVI_SECRET_DIR
BOVI_PRIVATE_DIR ?= $(HOME)/.local/share/bovicierre-academic
export BOVI_PRIVATE_DIR
BOVI_TEST_VENV ?= $(HOME)/.cache/bovicierre/sql-tests
BOVI_PYTHON = $(BOVI_TEST_VENV)/bin/python
export BOVI_TEST_VENV

setup-tools:
	@test -x "$(BOVI_PYTHON)" || python3 -m venv "$(BOVI_TEST_VENV)"
	"$(BOVI_PYTHON)" -m pip -q install -r db/requirements.txt

doctor:
	python3 scripts/doctor.py

academic:
	python3 scripts/academic.py

dev:
	python3 scripts/dev.py

demo: setup-tools
	"$(BOVI_PYTHON)" db/seed/demo.py

backup: setup-tools
	@test -n "$(BACKUP_DIR)" || (echo "Indica BACKUP_DIR privado fuera del repo"; exit 1)
	"$(BOVI_PYTHON)" scripts/recovery.py backup --directory "$(BACKUP_DIR)"

restore-check: setup-tools
	@test -n "$(BACKUP_DIR)" || (echo "Indica BACKUP_DIR existente"; exit 1)
	"$(BOVI_PYTHON)" scripts/recovery.py restore-check --directory "$(BACKUP_DIR)"

verify: verify-docs
	./backend/mvnw -q -f backend/pom.xml verify
	npm --prefix frontend run build
	npm --prefix frontend test
	python3 tools/esquema/comparar_catalogo.py
	python3 tools/esquema/comparar_catalogo.py --container bovicierre-academic-pg-b-1

verify-sql: setup-tools
	sh db/tests/prepare.sh
	sh db/tests/run.sh

verify-release-local: setup-tools
	python3 scripts/verify_release_local.py

verify-api:
	BOVI_API_IT=true BOVI_API_TEST_URL="$${BOVI_API_TEST_URL:-http://localhost:15180/api/v1}" BOVI_TEST_PASSWORD_FILE="$(BOVI_SECRET_DIR)/demo_password" ./backend/mvnw -q -f backend/pom.xml verify

verify-docs:
	python3 tools/verificar_cobertura.py
	python3 tools/esquema/esquema.py
	python3 -m unittest discover -s tools/diagramas -p 'test_*.py'
	npx -y @redocly/cli@1.34.5 lint docs/api/openapi.yaml
	python3 tools/api/route_coverage.py

stop:
	docker compose -p bovicierre-academic -f infra/compose/compose.academic.yml -f infra/compose/application.yml stop
