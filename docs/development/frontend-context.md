# Contexto frontend

El frontend local está implementado en `frontend/` con React 19.2.4, TypeScript 5.9.3 y Vite 8.0.3; las dependencias están fijadas en `package-lock.json`. El cliente de tipos se genera desde el contrato **OpenAPI 0.2.0** mediante `npm --prefix frontend run generate:api`, en `frontend/src/generated/api-schema.ts`. El contrato pertenece al coordinador; cambios de DTO deben coordinarse antes de regenerar el cliente.

## Acceso y entorno

La entrada integrada es **http://localhost:15180**, publicada únicamente en loopback por Caddy/Docker; su arranque y verificación integrada corresponden al coordinador. La alternativa de desarrollo es **http://127.0.0.1:15173** mediante Vite, con proxy `/api` a la API local **18080**. No ejecutar simultáneamente dos backends sobre 18080. Comandos de arranque: [README](../../README.md). El cierre UI integrado ejecutó15 casos por Caddy15180, seguidos de un caso adicional con caída física del proveedor. La tanda histórica de nueve casos por Vite15173 queda identificada como V11.

La sesión usa cookie del servidor y CSRF en memoria. No se guardan contraseñas ni tokens de sesión en almacenamiento del navegador. El acceso real sigue CSRF anónimo → login → selección de sede; las credenciales DEMO se obtienen del directorio privado local, sin copiarlas a documentación o código.

## Reglas de integración

- Cada ruta de negocio incluye la sede. El contenido se remonta al cambiar operación o sede; `AbortController` cancela los GET pendientes y evita aplicar resultados de un expediente anterior.
- Un resultado incierto conserva clave de idempotencia, cuerpo y versión. El intento en `sessionStorage` se separa por principal, sede y ruta. Tras recarga o nueva autenticación del mismo usuario, se consulta primero el resultado del comando; otro usuario no recupera ese intento.
- Las altas de usuario y archivos persisten solamente clave y huella del contenido; contraseña y bytes del archivo permanecen en memoria y pueden requerir recaptura idéntica después de recargar.
- Dinero canónico `{importe:string, moneda:"MXN"}` y peso `{kg:string}`. El navegador conserva decimales exactos y muestra cálculos del servidor; no suma totales financieros mediante coma flotante.
- Las ventas por kg resuelven posiciones a identidades animales canónicas antes de enviar el ticket. Editar un lote conserva su orden e identidad. La consulta FDW usa lector A y captura en el propietario de la sede; la interfaz acepta el snapshot antes de registrar el gasto.

Diseño vigente: [sistema visual](../ui/design-system.md), [flujos y pantallas](../ui/flows-and-screens.md) y [manual de usuario](../ui/user-manual.md). Fondo `#F6F7F4`, texto `#17211B`, acciones `#1F5A43`, tipografía de sistema e importes tabulares. Los datos mostrados vienen del backend; la demostración está identificada como sintética.

## Comprobación actual

- **13 pruebas unitarias PASS**, comprobación TypeScript y build PASS. Cliente regenerado desde OpenAPI 0.2.0, incluido diagnóstico de integración.
- **15/15 E2E PASS** por Caddy15180, PostgreSQL V13, Chrome visible con perfil temporal separado; duración global CLI1,3min (redondeada), casos exactos73.520ms en conjunto. **1/1 adicional PASS** de caída física y recuperación del proveedor, tanda47.431,536ms. Cero skips/retries. Compra → recepción → venta → liquidación → cobro → ajuste atómico → reembolso; archivos privados/revisión/QR, gastos/FDW, acuerdos versionados, cierre/reapertura y permisos AUDITOR.
- Regresiones verificadas: dos lotes editados antes y después de ticket aprobado; venta KG de 300.000 kg por 3000.00 MXN; respuesta de POST real 201 entregada como 502 y recuperada sin otro POST; GET pendiente B cancelado al cambiar a A.
- Predios: alta/validación/búsqueda/paginación20+1 y refresh. Ficha: entrega/recompra con dos ciclos conservados, paginación20/costoSQL. Corrección de ticket aprobado100→110kg con motivo/original conservado; comparación incompatible. Reservas: conflicto entre dos operadores y vencimiento real409; cartera/margen con corte/fuente y CSV toda sede, sin filtro local.
- Flujo completo compra→recepción→reserva/venta→cobro/aplicación a390px sólo con teclado:534 eventos/364Tab, sin ratón ni locator.focus. Capturas390/768/1440 sin desbordamiento global. GPU real **Intel integrada**, renderer `ANGLE (Intel, Mesa Intel(R) Graphics (RPL-P), OpenGL ES 3.2 Mesa 25.2.8-0ubuntu0.24.04.2)`, `ANGLE_OPENGL`; sin SwiftShader. No es prueba en teléfono físico ni benchmark de FPS.

Evidencia: [recorrido y capturas](../testing/evidence/ui/frontend-ui-tests.md), [resumen de15+1 E2E](../testing/evidence/ui/bovicierre-ui-final-run.json), [revisión y cierre de seis hallazgos](../testing/evidence/review-frontend-integration.md). Los resultados se refieren a estas ejecuciones; el resumen actual incluye la comprobación integrada por Caddy15180; las verificaciones del despliegue y backend pertenecen al coordinador.
