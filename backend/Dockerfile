FROM eclipse-temurin:21-jdk@sha256:3e3c176ffed168beb42c607be9bc1639b466cf00261a0fb04425562c9d0c5c2b AS build
WORKDIR /build
COPY backend/.mvn .mvn
COPY backend/mvnw backend/pom.xml ./
RUN chmod +x mvnw && ./mvnw -B -q dependency:go-offline
COPY backend/src src
# La prueba de precisión monetaria inspecciona también las fuentes del frontend.
COPY frontend/src /frontend/src
RUN ./mvnw -B -q package

FROM eclipse-temurin:21-jre@sha256:cff19e6215689161eb6162c11b86b0c60ddf802164f2eaf48d570f8fb79a36c5
# pebble (gestor de servicios de Ubuntu) no se usa y arrastra CVE de Go (Trivy 13-oct-2026).
RUN rm -f /usr/bin/pebble
RUN (getent group 1000 >/dev/null || groupadd --gid 1000 bovi) && (getent passwd 1000 >/dev/null || useradd --uid 1000 --gid 1000 --create-home bovi)
WORKDIR /app
COPY --from=build --chown=1000:1000 /build/target/bovicierre-0.1.0-SNAPSHOT.jar /app/bovicierre.jar
# El entrypoint puede ejecutarse como root (Railway): propiedad de root y sin escritura, para que el proceso 1000 no lo altere.
COPY --chown=0:0 backend/container-entrypoint.sh /app/entrypoint.sh
RUN chmod 555 /app/entrypoint.sh && mkdir -p /app/run /app/private-documents && chown -R 1000:1000 /app/run /app/private-documents && chmod 700 /app/run /app/private-documents
USER 1000:1000
ENV BOVI_BIND_ADDRESS=0.0.0.0 BOVI_RUNTIME_DIR=/app/run BOVI_DOCUMENTS_DIR=/app/private-documents
EXPOSE 18080
ENTRYPOINT ["/app/entrypoint.sh"]
