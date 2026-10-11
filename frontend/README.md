# Frontend de BoviCierre

React 19.2.4, TypeScript 5.9.3 y Vite 8.0.3. Node compatible: 20.20.2 (verificado) o 24.21.0. Dependencias fijadas en `package-lock.json`.

```sh
cd frontend
npm ci
npm run generate:api
npm run typecheck
npm test
npm run build
npm run dev
```

La entrada integrada es `http://localhost:15180` mediante Caddy. Como alternativa de desarrollo, Vite sirve `http://127.0.0.1:15173` y redirige `/api` al backend local `http://127.0.0.1:18080`. No hay credenciales incluidas en el frontend. El usuario necesita una cuenta del backend y una sede autorizada.

Sesión en cookie HttpOnly, CSRF únicamente en memoria. Un intento de comando guarda su clave, ruta con sede y contenido en `sessionStorage` de la pestaña para conservar el reintento después de recargar; se elimina al resolver la solicitud. Al expirar o terminar la sesión permanece aislado por principal, sede y ruta; solamente el mismo usuario autenticado puede recuperarlo. Nunca se guardan contraseñas ni tokens de sesión. Captura protegida hasta conocer el resultado de red; el reintento es manual, con la misma clave y cuerpo. No se calculan saldos ni totales financieros en JavaScript.

Las rutas cubren las15 vistas documentadas y predios/gastos/periodos/documentos. La ficha consulta ciclos de la sede por animal,20porpágina, con costos del servidor; cartera/margen/inventario permiten CSV de toda la sede sin filtro local. Datos ausentes muestran «No disponible». Los importes recibidos mantienen sus cadenas decimales exactas. Las operaciones admiten múltiples lotes sin sustituir los demás al editar uno; pesos, reservas, cierre económico, movimiento físico y pago se registran mediante comandos separados.

`npm test` verifica formato decimal exacto, captura canónica, preservación del intento de red y etiquetas accesibles. Estas pruebas y el build no prueban el recorrido contra PostgreSQL ni la GPU del navegador; la evidencia visual/integrada se registra desde la coordinación principal.

`npm run test:e2e` recorre formularios contra la API y PostgreSQL locales mediante Chrome con ventana visible y perfil temporal. Requiere el usuario DEMO y su contraseña fuera del repositorio en `~/.local/share/bovicierre-academic/secrets/demo_password`; genera únicamente datos sintéticos y evidencia en `/tmp/bovicierre-*`. Ejecutar sólo durante una ventana coordinada con backend y base de datos. No hay trazas, cookies ni contraseñas versionadas.

La imagen estática se prepara con `docker build -t bovicierre-frontend:local frontend` desde la raíz. El Dockerfile usa `npm ci`, compila con Node 24.21.0 y sirve el resultado con nginx unprivileged 1.29.5 en 8080 como UID/GID 101. La ruta `/api` corresponde al proxy central; el servidor estático no contiene credenciales ni conecta directamente a PostgreSQL. No se publica ninguna imagen.


Cierre integrado:13unitarias y15+1E2E PASS sobreV13, Chrome visible Intel; evidencia y límites en [recorrido](../docs/testing/evidence/ui/frontend-ui-tests.md). Los15 casos normales se ejecutan así durante una ventana coordinada:

```sh
BOVI_UI_TEST_URL=http://127.0.0.1:15180 npm run test:e2e -- closure.spec.ts additional.spec.ts keyboard.spec.ts
```

El caso físico del proveedor requiere coordinación externa de stop/start y los archivos de handshake `/tmp/bovicierre-provider-ui-ready` y `/tmp/bovicierre-provider-ui-resumed` (contenido exacto `resumed` después de verificar salud). El runner nunca detiene servicios. Sin `BOVI_PROVIDER_OUTAGE=true`, ese caso queda omitido expresamente; no se presenta como PASS. La tanda final lo ejecutó por separado con esa variable, sin omisiones.
