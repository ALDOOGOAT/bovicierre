.PHONY: doctor academic dev demo demo-profesor verify-academic evidence release-academic verify verify-docs verify-api verify-sql verify-release-local setup-tools backup restore-check stop

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

# Cierre académico. verify-academic = puerta local completa (la etapa sql incluye infra_evidence.py).
verify-academic: verify-release-local

demo-profesor: academic demo
	@echo "Demo lista en http://localhost:15180 (usuarios demo.admin/operador/caja/auditor)."
	@echo "Contraseñas en $(BOVI_SECRET_DIR)/demo_*password: entregarlas sólo por canal privado. Guion: docs/academic/guion-defensa.md"

evidence:
	@gate=$$(ls -d docs/testing/evidence/release-local/*/ | sort | tail -1); out=docs/testing/evidence/academic-release; mkdir -p $$out; \
	cp "$$gate/release-gate.json" $$out/release-gate.json && cp db/tests/*-result.json $$out/ && echo "Evidencia de $$gate copiada a $$out"

release-academic:
	@test -z "$$(git status --porcelain --untracked-files=no)" || (echo "Hay cambios sin commit: el paquete se arma sólo desde un commit"; exit 1)
	@mkdir -p dist; name=bovicierre-academico-$$(git rev-parse --short HEAD); \
	git archive --format=tar.gz --prefix=$$name/ -o dist/$$name.tar.gz HEAD && \
	if tar -xOzf dist/$$name.tar.gz | grep -aEq -- '-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[bp]-[A-Za-z0-9-]{10,}'; then echo "Posible secreto en el paquete: revisar"; rm dist/$$name.tar.gz; exit 1; fi && \
	(cd dist && sha256sum $$name.tar.gz > $$name.tar.gz.sha256) && echo "dist/$$name.tar.gz (sin secretos detectados) y su SHA-256"

stop:
	docker compose -p bovicierre-academic -f infra/compose/compose.academic.yml -f infra/compose/application.yml stop
