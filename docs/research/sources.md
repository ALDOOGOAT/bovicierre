# Fuentes

Columnas: ID · autor/institución · título · URL · tipo · consulta · afirmación respaldada · alcance/limitación · verificación del enlace.

- **Tipo**: COM = sitio comercial del proveedor (afirmaciones de marketing); OFI = documento oficial/normativo; ACA = académico; TEC = documentación técnica del motor/herramienta; MET = metodología.
- **Consulta**: fecha en que se leyó. "2026-10-11 (MP)" = fecha de corte declarada en el megaprompt para la investigación previa; no ha sido releída por Claude en este repo.
- **Verificación**: `OK 2026-10-10` = Claude abrió la URL y comprobó la afirmación; `pendiente` = falta abrirla. Ninguna fuente valida demanda, ingresos ni la corrección de la implementación.

| ID | Autor / institución | Título | URL | Tipo | Consulta | Afirmación respaldada | Limitación | Verificación |
|---|---|---|---|---|---|---|---|---|
| F01 | EngordaMax | Sitio comercial | https://engordamax.mx/ | COM | 2026-10-11 (MP) | Anuncia compras, pesajes, merma, costos y utilidad | Afirmaciones del proveedor; no prueba demanda | pendiente |
| F02 | Agryxo / Agroapp | Sitio comercial | https://www.agryxo.com/ | COM | 2026-10-11 (MP) | Anuncia compraventa, inventario, cartera, margen y control de doble venta | Idem | pendiente |
| F03 | Strategyzer | The Business Model Canvas | https://www.strategyzer.com/library/the-business-model-canvas | MET | 2026-10-11 (MP) | Nueve bloques del Canvas | Marco de hipótesis, no validación | pendiente |
| F04 | DOF / SIDOF | NOM-001-SAG/GAN-2015 (identificación de animales; SINIDA) | https://sidof.segob.gob.mx/notas/docFuente/5394324 | OFI | 2026-10-11 (MP) | Sistema de identificación, registros de ingreso/salida | Revisar modificaciones posteriores | pendiente |
| F05 | Secretaría de Economía | Catálogo de la NOM-001-SAG/GAN-2015 | https://platiica.economia.gob.mx/normalizacion/nom-001-sag-gan-2015/ | OFI | 2026-10-11 (MP) | Estado vigente de la norma | Revalidar | pendiente |
| F06 | DOF / SIDOF | Acuerdo DINESA, 2-dic-2025 | https://sidof.segob.gob.mx/notas/docFuente/5774853 | OFI | 2026-10-11 (MP) | Medidas diferenciadas de movilización (gusano barrenador) | No sustituye disposiciones posteriores | pendiente |
| F07 | SENASICA | SINACAM — consulta de requisitos | https://sistemasssl.senasica.gob.mx/SINACAMWeb/pages/consulta/requisitos/inicio.xhtml | OFI | 2026-10-11 (MP) | Consulta oficial de requisitos de movilización | Sin API pública verificada | pendiente |
| F08 | Poder Judicial de Chiapas | Ley de Fomento y Sanidad Pecuaria (PDF, últ. reforma 19-abr-2023) | https://www.poderjudicialchiapas.gob.mx/storage/legislacion/584C1A2A-3BB9-4D04-9073-40767B7624EF.pdf | OFI | 2026-10-11 (MP) | Marco estatal pecuario | Revisar reformas posteriores | pendiente |
| F09 | SAT | Proveedores autorizados de certificación de CFDI | https://www.sat.gob.mx/portal/public/tramites/lista-de-proveedores-autorizados-de-certificacion-de-cfdi | OFI | 2026-10-11 (MP) | Proceso fiscal válido requiere PAC | Liquidación interna ≠ CFDI | pendiente |
| F10 | Cámara de Diputados | LFPDPPP | https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf | OFI | 2026-10-11 (MP) | Tratamiento de datos personales por particulares | Verificar texto vigente | pendiente |
| F11 | Oklahoma State University Extension | Managing Shrink and Weighing Conditions in Beef Cattle | https://extension.okstate.edu/fact-sheets/managing-shrink-and-weighing-conditions-in-beef-cattle | ACA | 2026-10-11 (MP) | Factores que afectan la variación de peso | No fija descuento comercial universal | pendiente |
| F12 | Peter P. Chen (1976), MIT DSpace | The Entity-Relationship Model — Toward a Unified View of Data. DOI 10.1145/320434.320440 | https://dspace.mit.edu/entities/publication/5f4dcb94-111c-4368-8374-cec8842dee1d | ACA | 2026-10-11 (MP) | Fundamento del MER | — | pendiente |
| F13 | E. F. Codd (1970), IBM Research | A Relational Model of Data for Large Shared Data Banks. DOI 10.1145/362384.362685 | https://research.ibm.com/publications/a-relational-model-of-data-for-large-shared-data-banks | ACA | 2026-10-11 (MP) | Modelo relacional | — | pendiente |
| F14 | TU München | Material de modelado ER (DBfA) | https://db.in.tum.de/~grust/teaching/ss08/DBfA/db1-03.pdf | ACA | 2026-10-11 (MP) | Participación, cardinalidad (mín,máx) | Material de curso | pendiente |
| F15 | Rensselaer Polytechnic Institute | BCNF, 3NF y ER (lecture 7) | https://www.cs.rpi.edu/~sibel/csci4380/fall2026/lecture_notes/lecture7.html | ACA | 2026-10-11 (MP) | Descomposición, unión sin pérdida, preservación de DF | Material de curso | pendiente |
| F16 | Kanban University / Kanban Guides | The Kanban Guide (mayo 2025) | https://kanbanguides.org/the-kanban-guide | MET | 2026-10-11 (MP) | Flujo, políticas, WIP | Límites concretos son política local | pendiente |
| F17 | Michael Nygard | Documenting Architecture Decisions | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | MET | 2026-10-11 (MP) | Estructura de ADR | — | pendiente |
| F18 | Spring | Spring Boot — System Requirements | https://docs.spring.io/spring-boot/system-requirements.html | TEC | 2026-10-10 | "Spring Boot 4.1.1 requires at least Java 17 and is compatible with versions up to and including Java 26"; Maven ≥3.6.3 | Fijar patch al implementar | OK 2026-10-10 |
| F19 | Spring | Spring Framework — JDBC Core | https://docs.spring.io/spring-framework/reference/data-access/jdbc/core.html | TEC | 2026-10-11 (MP) | JdbcTemplate y SQL explícito | — | pendiente |
| F20 | PostgreSQL GDG | PostgreSQL 18 — Constraints | https://www.postgresql.org/docs/18/ddl-constraints.html | TEC | 2026-10-11 (MP) | CHECK no debe consultar otras filas | — | pendiente |
| F21 | PostgreSQL GDG | PostgreSQL 18 — Explicit Locking | https://www.postgresql.org/docs/18/explicit-locking.html | TEC | 2026-10-11 (MP) | Locks de fila, deadlocks | — | pendiente |
| F22 | PostgreSQL GDG | PostgreSQL 18 — CREATE SUBSCRIPTION | https://www.postgresql.org/docs/18/sql-createsubscription.html | TEC | 2026-10-11 (MP) | `origin`, `copy_data`, `create_slot` | `origin=none` no resuelve conflictos | pendiente |
| F23 | PostgreSQL GDG | Logical Replication — Restrictions | https://www.postgresql.org/docs/18/logical-replication-restrictions.html | TEC | 2026-10-11 (MP) | DDL, secuencias, large objects no se replican | — | pendiente |
| F24 | PostgreSQL GDG | Logical Replication — Architecture | https://www.postgresql.org/docs/18/logical-replication-architecture.html | TEC | 2026-10-11 (MP) | Apply y triggers | — | pendiente |
| F25 | PostgreSQL GDG | Client Connection Defaults | https://www.postgresql.org/docs/18/runtime-config-client.html | TEC | 2026-10-11 (MP) | `session_replication_role` y triggers/FK | — | pendiente |
| F26 | PostgreSQL GDG | Logical Replication — Security (y ddl-rowsecurity) | https://www.postgresql.org/docs/18/logical-replication-security.html | TEC | 2026-10-11 (MP) | Identidad del apply, RLS | — | pendiente |
| F27 | PostgreSQL GDG | postgres_fdw | https://www.postgresql.org/docs/18/postgres-fdw.html | TEC | 2026-10-11 (MP) | Foreign tables; sin 2PC remoto | — | pendiente |
| F28 | Pgpool Global Development Group | Clustering mode (raw) | https://www.pgpool.net/docs/latest/en/html/runtime-config-running-mode.html | TEC | 2026-10-11 (MP) | Modo raw no sincroniza ni balancea | — | pendiente |
| F29 | Docker | Official Image — postgres | https://hub.docker.com/_/postgres | TEC | 2026-10-11 (MP) | PGDATA y montaje en PG18 | Fijar digest | pendiente |
| F30 | Docker | Compose in production | https://docs.docker.com/compose/how-tos/production/ | TEC | 2026-10-11 (MP) | Despliegue con Compose | Un host = un dominio de fallo | pendiente |
| F31 | Docker | Compose secrets | https://docs.docker.com/compose/how-tos/use-secrets/ | TEC | 2026-10-11 (MP) | Secretos como archivos | No cifra los archivos fuente | pendiente |
| F32 | Caddy | Automatic HTTPS | https://caddyserver.com/docs/automatic-https | TEC | 2026-10-11 (MP) | TLS automático | Requiere DNS/puertos | pendiente |
| F33 | DigitalOcean | Droplet pricing | https://www.digitalocean.com/pricing/droplets | COM | 2026-10-11 (MP) | Basic 4 vCPU/8 GiB USD 48/mes | Precio no garantizado | pendiente |
| F34 | PostgreSQL GDG | pg_dump | https://www.postgresql.org/docs/18/app-pgdump.html | TEC | 2026-10-11 (MP) | Exclusión de publicaciones/suscripciones | — | pendiente |
| F35 | PostgreSQL GDG | Continuous Archiving and PITR | https://www.postgresql.org/docs/18/continuous-archiving.html | TEC | 2026-10-11 (MP) | Backups base + WAL | — | pendiente |
| F36 | Graphify-Labs | Repositorio graphify | https://github.com/Graphify-Labs/graphify | TEC | 2026-10-11 (MP) | Paquete `graphifyy`, ejecutable `graphify` | Instalado localmente 0.9.49 (verificado con `pipx list`) | parcial: paquete verificado |
| F37 | Graphify | CLI reference | https://docs.graphify.com/reference/overview | TEC | 2026-10-11 (MP) | Comandos | Contrastado con `graphify --help` local | pendiente |
| F38 | Graphify | Incremental updates | https://docs.graphify.com/guides/incremental-updates | TEC | 2026-10-11 (MP) | `--update` semántico vs. `graphify update` de código | — | pendiente |
| F39 | Graphify | Configuration | https://docs.graphify.com/reference/configuration | TEC | 2026-10-11 (MP) | Alcance/exclusiones | `.graphifyignore` = sintaxis gitignore (verificado en `graphify/detect.py` local) | parcial |
| F40 | Graphify | Team workflows | https://docs.graphify.com/guides/team-workflows | TEC | 2026-10-11 (MP) | Grafos por worktree | — | pendiente |
| F41 | Anthropic | Claude Code — Memory | https://code.claude.com/docs/en/memory | TEC | 2026-10-11 (MP) | CLAUDE.md breve y específico | — | pendiente |
| F42 | Anthropic | Claude Code — Skills | https://code.claude.com/docs/en/skills | TEC | 2026-10-11 (MP) | Skills y slash commands | — | pendiente |
| F43 | Graphviz | Node shapes | https://graphviz.org/doc/info/shapes.html | TEC | 2026-10-11 (MP) | Shapes para diagramas | Graphviz no instalado | pendiente |
| F44 | GitHub | About tasklists | https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists | TEC | 2026-10-11 (MP) | Sintaxis `- [ ]` | `[ ]` en tablas no es interactivo | pendiente |
| F45 | Meta / React | React Quick Start | https://react.dev/learn | TEC | 2026-10-11 (MP) | Frontend propuesto | — | pendiente |
| F46 | Vite | Getting Started | https://vite.dev/guide/ | TEC | 2026-10-10 | "Vite requires Node.js version 20.19+, 22.12+"; versión documentada 8.3.4 | — | OK 2026-10-10 |
| F47 | Testcontainers | PostgreSQL module | https://java.testcontainers.org/modules/databases/postgres/ | TEC | 2026-10-11 (MP) | PostgreSQL real en pruebas | Requiere Docker | pendiente |
| F48 | OpenStax / Rice University | Principles of Financial Accounting 10.1 | https://openstax.org/books/principles-financial-accounting/pages/10-1-describe-and-demonstrate-the-basic-inventory-valuation-methods-and-their-cost-flow-assumptions | ACA | 2026-10-11 (MP) | Identificación específica del costo | No dicta tratamiento fiscal del ganado | pendiente |
| F49 | OpenStax / Rice University | Principles of Managerial Accounting 3.1 | https://openstax.org/books/principles-managerial-accounting/pages/3-1-explain-contribution-margin-and-calculate-contribution-margin-per-unit-contribution-margin-ratio-and-total-contribution-margin | ACA | 2026-10-11 (MP) | Contribución y rango relevante | Ejemplos de EE. UU. | pendiente |
| F50 | Pgpool Global Development Group | Página principal pgpool.net | https://www.pgpool.net/mediawiki/index.php/Main_Page | TEC | 2026-10-10 | Versiones 4.7.3, 4.6.8, 4.5.13… publicadas 2026-09-29 con correcciones de seguridad | No indica versiones de PG soportadas | OK 2026-10-10 |

Si un enlace deja de estar disponible: buscar la ubicación oficial, registrar la sustitución aquí con fecha y no reutilizar el ID para otra fuente.
