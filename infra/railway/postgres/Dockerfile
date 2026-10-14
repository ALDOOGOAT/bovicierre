# PostgreSQL 18 para Railway: misma imagen y parámetros que compose.academic.yml (wal_level=logical para la réplica M–M),
# más TLS con certificado autofirmado porque el proxy TCP público de Railway no cifra.
FROM postgres:18-alpine@sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873
RUN apk add --no-cache openssl
COPY tls-entrypoint.sh /usr/local/bin/tls-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/tls-entrypoint.sh"]
CMD ["postgres", "-c", "wal_level=logical", "-c", "max_replication_slots=12", "-c", "max_wal_senders=12", "-c", "max_connections=50", "-c", "shared_buffers=128MB", "-c", "work_mem=4MB", "-c", "maintenance_work_mem=64MB", "-c", "max_slot_wal_keep_size=2GB", "-c", "ssl=on", "-c", "ssl_cert_file=/var/lib/postgresql/certs/server.crt", "-c", "ssl_key_file=/var/lib/postgresql/certs/server.key", "-c", "listen_addresses=*"]
