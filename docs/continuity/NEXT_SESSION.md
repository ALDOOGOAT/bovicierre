# NEXT_SESSION — cierre académico (mandato 2.0)

**Estado al 13-oct-2026:** rama `feature/cierre-academico-v1`, integrada en `main` y publicada en GitHub (`f9f32b5`, 13-oct-2026). Stack local en http://localhost:15180, A/B en V21. Entrega: `docs/academic/entrega-final.md`.

## Hecho (verificado localmente)
F1–F5 sin UUID (V19); CHECK→422; GOLD-ACAD-01/02/03 (V20 BV402); tablero de pendientes + guía; selección paginada; restablecer contraseña (V21); instalación vacía; TEST-40 Pgpool/réplica/corte/FDW; restore tras V21; skills `.claude/skills/bovicierre-*`; make `verify-academic|demo-profesor|evidence|release-academic`; competitive-review, SOLID, guion, 12 preguntas, aceptación; manual 23.10.

## Bloqueos que requieren al usuario
1. `RUBRICA_ORIGINAL_PIZARRON.png` → copiar a `docs/academic/rubrica.png`, registrar SHA-256 y procedencia, revisar AC-01..09 contra la foto.
2. Despliegue: destino, credenciales y presupuesto autorizados (o confirmar que basta la demo local).
3. Revisión humana de Aldo/Jared (`docs/academic/aceptacion-final.md`) y decisión de push/merge.

## Siguiente acción ejecutable
- Con la rúbrica: incorporarla y ajustar la matriz.
- `/graphify . --update` semántico para los documentos nuevos; `graphify label`.
- Opcional: cerrar sesiones abiertas al restablecer contraseña (hoy se usa “Bloqueado”).
