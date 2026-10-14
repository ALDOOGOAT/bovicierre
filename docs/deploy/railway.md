# Despliegue académico en Railway

Proyecto Railway `bovicierre-academico` (entorno `production`). Misma topología que `infra/compose/`: ocho servicios en la red privada `*.railway.internal`; sólo Caddy tiene dominio público HTTPS. Procedimiento idempotente: `scripts/railway_deploy.sh infra|db|app` (ver encabezado del script).

| Servicio | Origen | Volumen |
|---|---|---|
| `pg-a`, `pg-b`, `pg-prov` | `infra/railway/postgres` (PostgreSQL 18.6, `wal_level=logical`, TLS autofirmado) | `/var/lib/postgresql` |
| `pgpool-a`, `pgpool-b` | `infra/pgpool` (Pgpool-II 4.7.3, modo raw, un backend) | — |
| `backend` | `backend/Dockerfile` (Java 21) | `/app/private-documents` |
| `frontend` | `frontend/` (nginx sin root) | — |
| `caddy` | `infra/caddy/Dockerfile.railway` | — |

## Variables de entorno (nombres; los valores viven en Railway y en el directorio privado)

| Servicio | Variables |
|---|---|
| `pg-*` | `POSTGRES_PASSWORD` (secreto `admin_password`), `POSTGRES_DB=bovicierre` |
| `pgpool-a/b` | `BOVI_PGPOOL_BACKEND=pg-a/b.railway.internal`; secretos `APP_A_PASSWORD`, `APP_B_PASSWORD`, `REPL_PASSWORD`, `WORKER_PASSWORD` |
| `backend` | `BOVI_DB_A_URL` (Pgpool A), `BOVI_DB_B_URL` (Pgpool B), `BOVI_AUTH_URL` (directo a `pg-a:5432`, excepción documentada), `BOVI_BIND_ADDRESS=::`, `BOVI_COOKIE_SECURE=true`, `JAVA_OPTS`, `RAILWAY_DOCKERFILE_PATH`, `RAILWAY_RUN_UID=0` (permiso del volumen); secretos `BOVI_DB_A_PASSWORD`, `BOVI_DB_B_PASSWORD`, `BOVI_AUTH_PASSWORD`, `BOVI_WORKER_PASSWORD` |
| `caddy` | `BOVI_API_UPSTREAM=backend.railway.internal:18080`, `BOVI_WEB_UPSTREAM=frontend.railway.internal:8080`, `RAILWAY_DOCKERFILE_PATH=Dockerfile.railway` |

Para ver los valores: panel de Railway → servicio → *Variables* (requiere tu cuenta), o `railway variable list --service <servicio>`.

## Dónde están contraseñas y cuentas (fuera del repositorio, permisos 0700/0600)

- Secretos de infraestructura del despliegue: `~/.local/share/bovicierre-academic/railway/secrets/` (uno por archivo; distintos de los del stack local).
- Cuentas personales de la entrega (aplicación y PostgreSQL), URL y contraseñas: `~/.local/share/bovicierre-academic/railway/entrega/accesos.md` (legible) y `accesos.json`. Se generan con `scripts/academic_users.py`; entregar sólo por canal privado.
- Usuarios DEMO del caso académico: `…/railway/secrets/demo_password` y `demo_{operador,caja,auditor}_password`.
- Hosts/puertos públicos de PostgreSQL (proxy TCP, TLS obligatorio): panel de Railway → `pg-a|pg-b|pg-prov` → *Settings* → *TCP Proxy*.

## Modelo de permisos

- Aplicación: `ADMIN` (equipo), `OPERADOR` + `CAJA` + `AUDITOR` (profesor) por sede; las reglas y el cálculo viven en SQL.
- PostgreSQL: cuentas personales con el rol `bovi_consulta` (V22/V23): lectura de `bovi` sin hashes de contraseña, sin escritura; en la tercera instancia, lectura de `proveedor`. Los roles técnicos (`bovi_app_a/b`, `bovi_auth`, `bovi_worker`, `bovi_repl`, `bovi_fdw_read`) no se entregan.

## Verificación

`scripts/verify_access.py` (TEST-42) contra `BOVI_PUBLIC_URL` y `BOVI_PG_TARGETS`; `db/tests/infra_evidence.py` documenta las mismas comprobaciones de Pgpool, réplica y FDW en local.

## Cifrado y privilegios (revisión de seguridad del 13-oct-2026)

- **Proxy TCP público → PostgreSQL:** TLS obligatorio (`sslmode=require` en bootstrap, migraciones, semilla y scripts). El certificado es autofirmado: `require` cifra pero no autentica al servidor; para fijarlo, descarga `server.crt` del servicio y usa `BOVI_PG_SSLMODE=verify-ca` con `PGSSLROOTCERT`.
- **Red privada `*.railway.internal`:** Railway la cifra entre servicios (WireGuard). Además, la conexión de autenticación del backend a `pg-a` exige TLS (`?sslmode=require`); Pgpool→PostgreSQL y la réplica lógica viajan sólo por la red privada.
- **Backend como root:** `RAILWAY_RUN_UID=0` existe sólo porque el volumen se monta propiedad de root. `backend/container-entrypoint.sh` ajusta el dueño del directorio de documentos y baja de inmediato a `1000:1000` con `setpriv --clear-groups --bounding-set=-all` antes de leer secretos o arrancar Java (verificado: `uid=1000`, sin grupos extra, `CapEff=0`).
