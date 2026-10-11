# ADR-009: Documentos privados, evidencia y revisión administrativa
- Estado: propuesto · 2026-10-10 · Reglas: RN-037
## Alternativas
1. Bytes en la BD (bytea) — infla respaldos y réplica.
2. **Puerto `DocumentStorage` con adaptador de volumen local privado** (dev/academic) y almacenamiento de objetos privado en piloto; metadatos + SHA-256 en BD.
## Decisión
Opción 2. Nombres internos aleatorios, validación de tamaño y MIME real, descarga autorizada; nueva versión = nuevo registro con `documento_previo_id`. Revisión apunta a versión exacta; rótulo "revisión administrativa registrada", nunca "autorizado por SENASICA".
## Consecuencias
+ Integridad verificable. − El respaldo debe incluir el volumen de documentos además de la BD.
