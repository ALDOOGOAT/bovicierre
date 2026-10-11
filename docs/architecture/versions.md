# Versiones de componentes

Fecha de corte: 2026-10-10 (America/Mexico_City). "Instalado" = comprobado en la máquina de Aldo con `--version`. "Objetivo" = versión que se fijará en BOM/lockfile/imagen al crear el componente; se confirma en la tarea indicada.

## Herramientas locales (comprobadas)

| Componente | Versión instalada | Comando | Uso |
|---|---|---|---|
| OpenJDK | 21.0.12.1 (2026-08-18) | `java --version` | Backend (Java 21 LTS) |
| Apache Maven | 3.8.7 | `mvn --version` | Sólo para generar el Maven Wrapper; el build usa `./mvnw` |
| Node.js | 20.20.2 | `node --version` | Frontend; cumple Vite ≥20.19 |
| npm | 10.8.2 | `npm --version` | Gestor de paquetes frontend (pnpm no instalado) |
| Docker Engine | 29.4.1 | `docker --version` | Contenedores |
| Docker Compose | v5.1.3 | `docker compose version` | Topología dev/academic |
| psql (cliente) | 18.3 (PGDG Ubuntu 24.04) | `psql --version` | Scripts y pruebas manuales |
| uv / pipx | 0.12.5 / 1.4.3 | `--version` | Herramientas Python aisladas |
| graphify (paquete `graphifyy`) | 0.9.49, Python 3.12.3 vía pipx | `pipx list` | Grafo de contexto (no es dependencia del runtime) |
| Graphviz `dot` | **no instalado** | `command -v dot` | Alternativa de diagramas (opcional) |
| draw.io CLI | **no instalado** | `command -v drawio` | Exportación de diagramas → se usa contenedor |

## Componentes del producto (objetivo)

| Componente | Versión objetivo | Fuente oficial consultada (2026-10-10) | Compatibilidad / nota | Licencia | Se fija en |
|---|---|---|---|---|---|
| Spring Boot | 4.1.1 | docs.spring.io/spring-boot/system-requirements.html: "Spring Boot 4.1.1 requires at least Java 17 and is compatible with versions up to and including Java 26"; Maven ≥3.6.3 | Java 21 dentro del rango | Apache-2.0 | `backend/pom.xml` (parent BOM) — TASK-A-008 |
| Maven Wrapper | Maven 3.9.x | maven.apache.org | ≥3.6.3 exigido por Boot | Apache-2.0 | `.mvn/wrapper/maven-wrapper.properties` |
| PostgreSQL servidor | 18.x (misma menor en A/B/FDW) | hub.docker.com/_/postgres; postgresql.org/docs/18 | PGDATA por defecto `/var/lib/postgresql/18/docker`, montar `/var/lib/postgresql` | PostgreSQL License | `infra/compose/*.yml` por digest — TASK-A-011 |
| Pgpool-II | 4.7.3 (publicada 2026-09-29, incluye correcciones de seguridad) | pgpool.net (página principal) | Confirmar soporte PG18 en notas de versión antes de fijar; alternativa 4.6.8 | BSD-like | imagen en compose — TASK-A-011 |
| Flyway | la gestionada por el BOM de Boot 4.1.1 | docs.spring.io | módulo `flyway-database-postgresql` | Apache-2.0 | `pom.xml` |
| Testcontainers | la gestionada por el BOM de Boot 4.1.1 | java.testcontainers.org | requiere Docker local | MIT | `pom.xml` |
| Vite | 8.x (doc muestra 8.3.4) | vite.dev/guide: "Vite requires Node.js version 20.19+, 22.12+" | Node 20.20.2 válido | MIT | `frontend/package-lock.json` — TASK-J-004 |
| React / TypeScript | versión que instale la plantilla `react-ts` de Vite 8 | react.dev | se fija en lockfile | MIT / Apache-2.0 | TASK-J-004 |
| Caddy | 2.x | caddyserver.com | HTTPS automático requiere DNS público | Apache-2.0 | TASK-A-028 |
| Redocly CLI | versión fijada al validar (`npx @redocly/cli@<x>`) | redocly.com | sólo herramienta de lint | MIT | TASK-A-007 |

## Política de actualización

1. Fijar versión exacta (BOM, lockfile o digest de imagen); nunca `latest`.
2. Actualizar por PR con: motivo, notas de versión leídas, `./mvnw verify` y `npm run build` en verde.
3. A y B siempre en la misma versión mayor de PostgreSQL; las migraciones se aplican coordinadas.
