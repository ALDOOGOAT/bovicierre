# ADR-008: Autenticación, permisos y aislamiento del piloto
- Estado: propuesto · 2026-10-10 · Reglas: RN-001
## Alternativas
1. JWT en localStorage — expuesto a XSS, revocación difícil.
2. **Sesión de servidor (Spring Security) con cookie HttpOnly/Secure/SameSite=Lax + CSRF, mismo origen.**
3. OIDC externo — no necesario para el piloto.
## Decisión
Opción 2. Sesiones locales no replicadas: si cae el nodo de sesiones se reautentica. Contraseñas con `DelegatingPasswordEncoder`. Piloto: una empresa por despliegue; empresa_id se conserva para crecer, sin vender multiempresa compartido hasta probar casos negativos.
## Consecuencias
+ Revocación inmediata. − Escritura en B requiere sesión válida (no se promete disponibilidad total si A cae).
