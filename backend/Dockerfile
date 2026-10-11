FROM eclipse-temurin:21-jdk@sha256:3e3c176ffed168beb42c607be9bc1639b466cf00261a0fb04425562c9d0c5c2b AS build
WORKDIR /build
COPY .mvn .mvn
COPY mvnw pom.xml ./
RUN chmod +x mvnw && ./mvnw -B -q dependency:go-offline
COPY src src
RUN ./mvnw -B -q package

FROM eclipse-temurin:21-jre@sha256:cff19e6215689161eb6162c11b86b0c60ddf802164f2eaf48d570f8fb79a36c5
RUN (getent group 1000 >/dev/null || groupadd --gid 1000 bovi) && (getent passwd 1000 >/dev/null || useradd --uid 1000 --gid 1000 --create-home bovi)
WORKDIR /app
COPY --from=build --chown=1000:1000 /build/target/bovicierre-0.1.0-SNAPSHOT.jar /app/bovicierre.jar
COPY --chown=1000:1000 container-entrypoint.sh /app/entrypoint.sh
RUN chmod 500 /app/entrypoint.sh && mkdir -p /app/run /app/private-documents && chown -R 1000:1000 /app/run /app/private-documents && chmod 700 /app/run /app/private-documents
USER 1000:1000
ENV BOVI_BIND_ADDRESS=0.0.0.0 BOVI_RUNTIME_DIR=/app/run BOVI_DOCUMENTS_DIR=/app/private-documents
EXPOSE 18080
ENTRYPOINT ["/app/entrypoint.sh"]
