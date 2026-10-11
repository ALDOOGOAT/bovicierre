# Ejemplo de configuración de producción

`production.example.yml` se combina, en este orden, con `compose.academic.yml` y `application.yml`. Es una preparación para revisión de una VM: no acredita despliegue, DNS, certificados emitidos ni seguridad operativa de un servidor público.

El ejemplo elimina los puertos publicados de los tres PostgreSQL y ambos Pgpool. Sólo Caddy publica TCP 80/443 y UDP 443; conserva el usuario sin privilegios, usa el archivo de Caddy del coordinador y activa `SPRING_PROFILES_ACTIVE=production` y `BOVI_ENV=production` en la API. Los secretos siguen siendo archivos externos. El proveedor incluido es una fuente **DEMO**, no una integración comercial.

Antes de cualquier arranque autorizado deben definirse `BOVI_DOMAIN`, `TLS_CONTACT_EMAIL`, `BOVI_SECRET_DIR`, `BOVI_PRIVATE_DIR`, `BOVI_UID` y `BOVI_GID` para esa VM. Sus directorios `private-documents`, `caddy-data` y `caddy-config` deben existir, pertenecer al UID/GID de la aplicación y tener permisos 0700; archivos de secretos, 0600. Los volúmenes persistentes de Caddy usan enlaces del controlador local a esos directorios privados: Compose no crea ni corrige su propietario. La configuración de `/tmp` utiliza el mismo UID/GID. No reutilizar las rutas, credenciales, proyecto ni volúmenes académicos del equipo local.

La inicialización comercial de roles, empresa, sedes, usuarios, contraseñas y `infra.nodo_config` exige un procedimiento autorizado independiente. No está suministrada por las semillas. `db/bootstrap/bootstrap.py` y `db/seed/demo.py` rechazan los indicadores `BOVI_ENV=production` o perfil Spring `production` antes de cualquier operación. El ejemplo no agrega servicios de bootstrap, migración o semilla automáticos. Las migraciones deberán ejecutarse como un trabajo separado, sobre una base y roles comerciales preparados y después de revisar el respaldo y la recuperación.

Para revisar únicamente la configuración, con valores y rutas propios de la VM:

```bash
docker compose -p bovicierre-production \
  -f infra/compose/compose.academic.yml \
  -f infra/compose/application.yml \
  -f infra/compose/production.example.yml config --quiet
```

Se requiere una versión de Docker Compose que soporte `!reset` y `!override`. La validación local se hizo con Compose 5.1.3, un dominio reservado `.invalid` y rutas privadas de revisión, sin arrancar contenedores ni resolver DNS. El archivo resuelto queda privado fuera del checkout; `db/tests/production-compose-result.json` registra las comprobaciones sin secretos.

Quedan pendientes inventario y recursos de VM, firewall, dominio autorizado, imagen/versionado del despliegue, credenciales comerciales y rotación, respaldo externo, prueba de restauración en el destino, autorización de arranque y pruebas reales de HTTPS/cookie segura. Los certificados y el estado TLS sólo se conservarán si se respaldan también los directorios persistentes de Caddy.
