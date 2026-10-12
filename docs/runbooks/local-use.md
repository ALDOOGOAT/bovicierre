# Empezar a usar BoviCierre en local

Fecha: 12-oct-2026. Interfaz integrada: **http://localhost:15180**. [Manual técnico completo, 239 páginas](../pdf/BoviCierre_Manual_Integral.pdf) y [manual de pantallas](../ui/user-manual.md).

## Arranque y acceso

Desde la raíz del checkout:

```bash
make doctor
make academic
```

Si los servicios ya funcionan, abre la URL; no necesitas reiniciarlos. Para cargar la semilla sintética reproducible en un entorno DEMO identificado, usa `make demo`. No borra datos ni introduce compras reales de un cliente.

En el login usa `demo.admin`. Su contraseña se genera en el archivo privado:

```bash
cat "$HOME/.local/share/bovicierre-academic/secrets/demo_password"
```

Consulta ese valor únicamente en la terminal local; no lo copies a Git, registros o capturas. Pulsa **Ingresar** y selecciona **DEMO Sede A**. El administrador puede consultar y ejecutar los flujos. También existen:

| Usuario | Rol | Archivo local de contraseña |
|---|---|---|
| demo.admin | ADMIN | demo_password |
| demo.operador | OPERADOR | demo_operador_password |
| demo.caja | CAJA | demo_caja_password |
| demo.auditor | AUDITOR | demo_auditor_password |

Los archivos están en el mismo directorio privado. En un checkout nuevo primero se generan mediante el bootstrap; no hay una contraseña pública fija. No reutilizar credenciales ni semilla DEMO para un piloto real.

## Primer recorrido recomendado

1. En **Operaciones**, abre un registro existente y distingue estado económico, entrega y saldo.
2. En **Inventario**, consulta animales, posición/ciclo, costo y disponibilidad.
3. En **Liquidaciones**, revisa base, cargos, abonos, aplicaciones y saldo.
4. En **Cobros y pagos**, diferencia dinero registrado, validado, aplicado y disponible.
5. En **Cartera**, observa obligaciones pendientes; en **Margen**, revisa venta, costo y gasto.
6. Abre el **Expediente** para localizar hechos, documentos y versiones.

## Crear tu propia prueba

1. Registra una contraparte y un animal DEMO, si aún no existen.
2. En **Nueva operación**, crea una compra. Para el primer ejercicio, elige precio **por cabeza**, selecciona animales y guarda el lote.
3. Acepta las condiciones. En **Revisar y confirmar**, elige un periodo abierto y una fecha dentro de su rango; confirma la compra.
4. Comprueba la obligación en Liquidaciones y las posiciones en Inventario.
5. Si la compra quedó pendiente de recepción, registra **RECEPCION** en **Recepción y entrega** antes de intentar vender.
6. Crea una venta con posiciones disponibles, guarda condiciones, reserva con vencimiento y confirma con periodo abierto.
7. Para documentar dinero, registra el pago/cobro, valídalo y aplícalo a una liquidación compatible.
8. Registra la entrega física aparte, cuando proceda. Confirmar venta, cobrar y entregar son hechos diferentes.

La comprobación del 12-oct encontró octubre de 2026 abierto en A y B. Esto es una observación, no una garantía permanente: si después cierras el periodo, las operaciones deben usar el periodo abierto que corresponda. No se cambia silenciosamente la fecha de un comando.

Si se pierde una respuesta, usa la recuperación del mismo intento. Si aparece conflicto de versión/reserva, recarga y revisa antes de generar una intención nueva. No supongas que un timeout significa que no hubo commit.

## Detener y reanudar

```bash
make stop
make academic
```

Stop conserva volúmenes y registros. La alternativa manual `make dev` requiere evitar API/Caddy concurrentes; consulta el README. No usar `down -v`, reset o borrados para abrir una sesión.

## Comprobación real y límites

[Registro de acceso](../testing/evidence/local-access-2026-10-12.json): ocho servicios activos, salud disponible para A/B/autenticación, login ADMIN HTTP204, sedes/periodos consultados y logout204. Se envió la apertura mediante `xdg-open` con exit0; no se inspeccionó visualmente esa pestaña porque las herramientas de navegador de la sesión no estuvieron disponibles. Las pruebas visuales anteriores se conservan en su propia evidencia.

Toda esta práctica usa datos sintéticos locales. No realiza cobros bancarios, autorizaciones sanitarias ni despliegue público.
