# Revisión humana — campaña UI/UX + QA (Aldo y Jared)

Las verificaciones técnicas locales están hechas y registradas; esta lista es lo que **sólo una persona** puede aprobar. Marcar cada casilla con nombre y fecha. Ningún agente marca esta lista.

## Cómo levantar y probar
```bash
make academic                       # levanta todo y conserva datos (http://localhost:15180)
make demo                           # opcional: recrea datos DEMO
make verify-release-local           # puerta técnica (~4 min)
```
Usuarios DEMO: `demo.admin`, `demo.operador`, `demo.caja`, `demo.auditor`; contraseñas en `~/.local/share/bovicierre-academic/secrets/` (nunca en el repo).

## Aldo — backend, base de datos, infraestructura
- [ ] Leer V14–V18 y confirmar que las transiciones permitidas coinciden con la operación real (DEC-13).
- [ ] Aprobar o rechazar el tope de 30 días para reservas (DEC-24, V18).
- [ ] Aprobar o rechazar ADR-018 (SF-09, riesgo aceptado con controles) y sus disparadores.
- [ ] Revisar que la fórmula canónica de margen es `fn_reporte` (DEC-12).
- [ ] Revisar MER y modelo relacional contra la matriz de coherencia (V14–V18 no cambian tablas ni columnas).
- [ ] Revisar el informe de dependencias y DAST (`docs/security/dependency-report.md`) y decidir cada hallazgo abierto.
- [ ] Ensayar `make backup` / `make restore-check` con un directorio propio.

## Jared — frontend y experiencia
- [ ] Recorrer en navegador, con cada rol: acceso → sede → Bandeja → nueva compra → condiciones → pesaje → confirmar → liquidación → cobro → aplicar → cartera → margen.
- [ ] Juzgar el pase visual v3 (UXD-12..20): tipografía, banda fotográfica, animaciones, legibilidad de cifras.
- [ ] Probar en un teléfono físico a 390 px y en tablet; activar «reducir movimiento» del sistema y confirmar que no hay animaciones.
- [ ] Probar con lector de pantalla (NVDA u Orca) acceso, una tabla y un formulario con error.
- [ ] Confirmar que textos, botones y mensajes de error son comprensibles para el operador real.

## Ambos
- [ ] Revisar el capítulo 23 del manual PDF y que ningún texto atribuya trabajo humano que no hicieron.
- [ ] Decidir si la rama `feature/uiux-qa-claude` se integra a `main` y cuándo se hace push.
- [ ] Decidir el despliegue: VM, dominio, TLS, credenciales comerciales y rotación, respaldo externo (ver veredicto en `docs/quality/final-report.md`).
