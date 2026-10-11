# Revisión independiente de recuperación y arranque

Revisión de sólo lectura de `scripts/recovery.py`, `scripts/academic.py` e `infra/compose/application.yml`. Se comprobaron el código actualizado y las evidencias finales del coordinador. Esta revisión no ejecutó respaldo, restauración, arranque ni parada; los resultados físicos citados pertenecen al ensayo del coordinador.

## Hallazgos cerrados

1. **Reanudación de la API propia después del respaldo.** La variable del contenedor de API se reutilizaba en el recorrido de los PostgreSQL. Ahora `api_container` conserva la identidad de la API y `restart` se activa inmediatamente después de detenerla, antes de comprobar su estado. La selección del proceso Java exige el directorio del backend, puerto 18080 y directorio de ejecución de la fuente; rechaza dos API simultáneas y excluye la API restaurada de 18180. Corrección comprobada por lectura. El ensayo final V13 también acredita reanudación y salud de la API propia en Docker.
2. **Integridad de las fuentes privadas antes de copiar.** El respaldo calcula los manifiestos de secretos y documentos antes de `copytree`, compara las copias y vuelve a comprobar las fuentes al terminar los volcados. `manifest()` rechaza enlaces simbólicos en el recorrido. Se cerró por lectura la debilidad anterior, que comprobaba únicamente el destino después de copiar. No se ejecutó una prueba negativa con sustitución concurrente de archivos.
3. **Parada del ensayo cuando falla la restauración.** El bloque de error solicita `stop` únicamente al proyecto nuevo creado para el ensayo y conserva sus volúmenes. No detiene la fuente ni ejecuta `down -v`. Corrección comprobada por lectura; no se inyectó un fallo para verificar físicamente esa rama. La orden de parada no comprueba su código de salida: si Docker deja de responder, la parada no está garantizada y requiere comprobación operativa.

## Controles comprobados

- Respaldo privado fuera del checkout: directorio 0700 y archivos de volcados, roles, manifiesto y secretos 0600. Secretos y documentos locales pertenecen al usuario y sus directorios son 0700. No se leyeron valores de credenciales. Los errores del proceso no propagan su salida privada ni cadenas de conexión.
- La pausa identifica y detiene la API propia, espera su terminación y exige cero transacciones cliente activas, cero entregas pendientes y firmas empresariales A/B convergentes. Las firmas locales conservan idempotencia, inbox, entregas, capturas y historial Flyway. Esta consistencia requiere que ningún otro escritor externo actúe durante la ventana.
- La restauración usa proyecto, red, volúmenes y puertos propios: 18432/18433/18434/18999/18998 en loopback. Verifica hashes de volcados, roles y documentos; conserva firmas empresariales y técnicas, invalida sesiones y recrea suscripciones mediante los alias de su propia red. No elimina ni reinicializa la fuente.
- La comprobación HTTP restaurada usa exclusivamente 18180, comprueba acceso con credenciales restauradas, hash del archivo privado, una compra nueva, replay con ETag original y consulta de idempotencia.
- El arranque académico rechaza una API manual en 18080, valida propietario/permisos de documentos y utiliza UID/GID explícitos y secretos en archivos. La aplicación local publica sólo Caddy en 15180 sobre loopback. No equivale a una configuración pública de producción.

## Evidencia física final V13

El coordinador ejecutó el respaldo y la restauración final sobre V13; se leyeron estos resultados:

- [backup-v13.json](recovery/backup-v13.json): pausa **8,038 segundos**, API propia en Docker reanudada y saludable antes del ensayo, copia de la revisión indicada con cambios de trabajo declarados (`dirty: true`).
- [restore-v13.json](recovery/restore-v13.json): restauración aislada en **28,616 segundos**, firmas y hashes coincidentes, sesiones invalidadas, idempotencia/inbox preservados y publicaciones recreadas. La prueba HTTP acredita compra nueva **1000,00**, archivo con el mismo hash, resultado idéntico con el ETag original, consulta de comando completado e inventario persistido.

El primer chequeo HTTP del inventario omitía el filtro por animal y sólo veía100 posiciones; se corrigió el harness y el recorrido recuperado volvió a pasar. La primera compra de ese ensayo quedó exclusivamente en la restauración aislada, sin reiniciar ni modificar hechos de la fuente. El coordinador confirmó parada de API18180 y del proyecto nuevo, con sus volúmenes conservados y fuente15180 saludable. Esta revisión leyó el resultado y el informe del ejecutor; no operó esos servicios.

Como antecedentes se conservan [backup-v11.json](recovery/backup-v11.json) y [restore-v11.json](recovery/restore-v11.json), pausa7,770s/restauración26,801s. No sustituyen el ensayo actual V13.

## Límites vigentes

El `finally` solicita reanudación de la API, pero no espera por sí mismo a que esté saludable. El resultado final V13 sí incluye esa comprobación posterior; no se generaliza a todos los caminos de error. La parada ante error de restauración y el rechazo de fuentes privadas cambiantes se verificaron en el código, sin inyección física de fallos.

El ensayo fue en el mismo equipo. No acredita recuperación ante pérdida de la laptop, copia externa, PITR, TLS público ni una VM comercial. El ejemplo de producción exige provisión comercial autorizada y bloquea bootstrap/semilla DEMO cuando se indican los perfiles de producción. No se detecta un bloqueante vigente para el procedimiento local con sus precondiciones; la aceptación humana y el despliegue externo siguen separados.
