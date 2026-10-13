FROM debian:bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev libssl-dev curl ca-certificates
RUN curl -fsSL 'https://www.pgpool.net/source/pgpool-II-4.7.3.tar.gz' -o /tmp/pgpool.tar.gz && echo '4bf9df3e13feb8e64bee486b4ea54c9076296c2d9406165b0b68d32086fce250  /tmp/pgpool.tar.gz' | sha256sum -c - && tar -xzf /tmp/pgpool.tar.gz -C /tmp
RUN cd /tmp/pgpool-II-4.7.3 && ./configure --with-openssl && make -j2 && make install
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 libssl3 postgresql-client && rm -rf /var/lib/apt/lists/* && mkdir -p /etc/pgpool2
COPY --from=build /usr/local /usr/local
COPY entrypoint.sh /entrypoint.sh
# Sin root (Trivy DS-0002): pool_passwd, pid y sockets viven en /tmp; Compose fija el UID que lee los secretos.
RUN useradd --system --uid 10001 --no-create-home pgpool
USER pgpool
ENTRYPOINT ["/entrypoint.sh"]
