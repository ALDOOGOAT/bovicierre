# Roadmap y metodología

## Metodología
Desarrollo incremental por casos completos con **Kanban** [F16] (no Scrum). Columnas: Backlog → Listo → En curso → Revisión → Hecho. Políticas (propuesta del equipo):
- WIP: 1 tarea de implementación por persona; 1 en revisión compartida.
- Entra a Listo con AC/RN, dependencias y criterio de aceptación.
- Integración diaria de incrementos pequeños; `main` siempre compila.
- Coordinación diaria de 15 min (contrato, bloqueos, siguiente integración).
- PR revisado por el otro integrante (autoría real).
- Un cambio de modelo se refleja en migración + contrato + pantalla.
- Métricas: tareas terminadas, bloqueos, tiempo de ciclo.

## Capacidad
21 días (11–31 oct 2026). Escenario: 4–6 h efectivas/día/persona = 168–252 h-persona. **Supuesto, no promesa.** Registro real:

| Semana | Aldo (h) | Jared (h) | Nota |
|---|---:|---:|---|
| 11–17 oct | — | — | |
| 18–24 oct | — | — | |
| 25–31 oct | — | — | |

## Hitos
| Fechas | Aldo | Jared | Criterio |
|---|---|---|---|
| 11–13 oct | Reglas, MER Chen, relacional, diccionario, ADR, OpenAPI, primer grafo | Usuarios, flujos, wireframes, términos | Paquete de diseño consistente y trazable |
| 13–14 oct | Migraciones/roles, experimento M–M/FDW, estructura auth | Proyecto frontend, sistema visual, mocks, sesión | Contrato compartido y topología verificada |
| 15–18 oct | Maestros, inventario, compra, pesajes, evidencia, costo inicial | Catálogos, ficha, captura de compra/pesajes | Compra → posición → liquidación integrada; grafo |
| 19–22 oct | Reserva, venta, valoración, gastos, pagos, ajustes, periodos | Venta, simulación, liquidación, pagos, conflictos | GOLD y concurrencia esencial demostrados |
| 23–25 oct | Reportes, auditoría, outbox, conciliación, pruebas réplica/FDW | Cartera, margen, expediente, QR, sincronización | Recorrido completo; grafo 24 |
| 26–28 oct | Staging, pipeline, backups, rendimiento, permisos | Responsive, accesibilidad, E2E, manual | Candidata desplegable + restauración ensayada; grafo 28 |
| 29–31 oct | Correcciones, evidencia SQL, manuales, ensayo, release | Correcciones, capturas, demo | Entrega reproducible; grafo final 31 |

Congelamiento de extras: 29-oct. Orden de recorte si hay retraso: OCR → offline → adornos visuales. Nunca se recorta: integridad, MER, roles, transacciones, replicación, FDW.
