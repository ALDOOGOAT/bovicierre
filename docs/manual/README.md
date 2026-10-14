# Manual técnico integral de BoviCierre

[Descargar el PDF completo](../pdf/BoviCierre_Manual_Integral.pdf): **254 páginas**, 24 capítulos, 319 marcadores y 320 enlaces. Manual preparado el 12-oct-2026 para Aldo y Jared sobre la revisión `92d3d41`, con el **capítulo 23 (págs. 229–240)** que documenta la campaña UI/UX y QA del mismo día: rediseño S1, endurecimiento SF-01..21, migraciones V14–V18, contrato DIV-11/12/13, decisiones semánticas DEC-12..25, pase visual v3, ADR-018, SCA/DAST, carga sostenida y veredicto de despliegue, pruebas nuevas, puerta local y recuperación. La sección 23.12 (14-oct-2026) documenta el rediseño ejecutivo v4 (bandas por sección, recorrido guiado, videos de uso, medición en Intel UHD) y el capítulo 22 usa capturas v4. La sección 23.11 coteja la rúbrica del pizarrón punto por punto y documenta cuentas personales, laboratorio `CREATE RULE`, FDW desde A y B y los hallazgos de seguridad SF-27..33 (V23–V26); el capítulo 24 lista los SHA-256 del código entregado (`docs/manual/refresh_hashes.py`). La sección 23.10 (13-oct-2026) añade el cierre académico: V19–V21, GOLD-ACAD, tablero de pendientes, restablecimiento de contraseña, instalación vacía y evidencia Pgpool/réplica/FDW (TEST-40), sobre la rama `feature/cierre-academico-v1`. Si el capítulo 23 difiere de uno anterior, prevalece el 23.

## Qué explica

- Problema del negocio, identidad animal, ciclo, compra, venta, recepción, entrega, obligaciones y dinero.
- Arquitectura implementada y diferencias respecto al diseño inicial: no presenta interfaces planeadas como clases existentes.
- Java: 24 unidades fuente, métodos, argumentos, campos, variables locales, filtros, permisos, JDBC, archivos, CSV, QR y worker.
- Frontend: 75 funciones detectadas, componentes, props, estado, formularios, navegación, CSRF, ETag, idempotencia y recuperación de resultados inciertos.
- Base de datos: 42 tablas lógicas y 4 técnicas adicionales; migraciones V1–V13, tipos, claves, funciones, variables, locks, periodos, réplicas, FDW y permisos.
- Contrato: las 70 operaciones HTTP y los 49 esquemas reutilizables, con parámetros, respuestas y restricciones.
- Reglas RN-001..045, fórmulas LaTeX y ejemplos GOLD, modelos, normalización, ADR y casos de uso.
- Comandos de arranque, configuración sin valores de secretos, pruebas, respaldo, restauración, diagnóstico y límites del piloto.
- Siete capturas reales y doce láminas vectoriales del repositorio.

## Alcance y verificación

El PDF es un corte del software, no una certificación ni una prueba nueva de toda la aplicación. Las pruebas citadas corresponden a las ejecuciones del 11-oct; la comprobación de acceso del 12-oct se conserva separadamente en [evidencia](../testing/evidence/local-access-2026-10-12.json).

Se compuso con Tectonic 0.17.0/LaTeX, se renderizaron sus 239 páginas, se revisaron contactos completos y páginas detalladas, se comprobó la geometría de los textos y se comparó el contenido extraído con las once credenciales privadas locales sin encontrar coincidencias. No se guardaron valores de esas credenciales. La última compilación no produjo avisos de texto desbordado ni caracteres faltantes. Registro y SHA-256: [verification.json](verification.json).

El documento conserva el estado de tareas previo al cambio de convención de casillas. Desde el 12-oct, por petición del usuario, `[x]` en el [backlog vigente](../project/backlog.md) significa verificación técnica local con evidencia, y la revisión humana se mantiene en su propia columna. Las 55 revisiones humanas siguen pendientes; esta actualización no cambia el código que explica el PDF.

## Reconstrucción desde el checkout

Fuente editable: [source/manual.tex](source/manual.tex); referencias de diagramas: [source/assets.json](source/assets.json). Las capturas y láminas se reutilizan desde `docs/testing/evidence/ui/` y `docs/diagrams/exports/`, sin duplicarlas en el directorio del manual. Los marcadores de rutas se resuelven en un directorio temporal externo al producto.

Requisitos auxiliares: Python 3, Tectonic 0.17.0 y las fuentes DejaVu Serif, DejaVu Sans y DejaVu Sans Mono. Tectonic puede descargar sus paquetes TeX en la primera compilación; necesita red o su caché previamente preparada. No forma parte de las dependencias de React o Java.

Desde la raíz:

```bash
python3 docs/manual/build.py --self-check
python3 docs/manual/build.py --output /tmp/BoviCierre_Manual_Integral.pdf
```

Sin `--output`, sustituye el PDF en `docs/pdf/`. La recompilación reconstruye el contenido y la navegación, pero los bytes pueden variar por fecha, versión de fuentes y metadatos; no se promete reproducibilidad binaria. El PDF publicado conserva la versión revisada y su huella en verification.json. Actualizar el contenido requiere editar la fuente, compilar, revisar el resultado y renovar ese registro.

Las copias de entrega de `output/` permanecen locales e ignoradas. Credenciales, dumps, perfiles y `.aws` no se incluyen en Git.
