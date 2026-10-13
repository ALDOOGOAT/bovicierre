# Caddy 2.11.7 recompilado con Go 1.27.2 y golang.org/x/net 0.60.0 (Trivy 13-oct-2026: CVE-2026-78667,
# CVE-2026-78669, CVE-2026-97031 en el binario oficial con Go 1.26.8). Retirar cuando upstream publique la versión.
FROM caddy:2.11.7-builder-alpine@sha256:d6161a2c82fd58b3205048958fb6246d0c5d892beee8a47e90944610c4efd100 AS build
RUN xcaddy build v2.11.7 --replace golang.org/x/net=golang.org/x/net@v0.60.0 --output /usr/bin/caddy-patched

FROM caddy:2.11.7-alpine@sha256:d8542f48d34a9cf4e4c11a478865229840e87e4c96ea3f439101f31a5d35f75f
COPY --from=build /usr/bin/caddy-patched /usr/bin/caddy
