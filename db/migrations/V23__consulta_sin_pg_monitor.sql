-- V23: revisión de seguridad de V22. pg_monitor incluye pg_read_all_stats, que deja ver el texto de consultas de
-- otras sesiones (pg_stat_activity), y durante el bootstrap ese texto puede llevar contraseñas literales.
-- Sin pg_monitor la cuenta de consulta conserva pg_stat_subscription, pg_replication_slots y pg_publication.
REVOKE pg_monitor FROM bovi_consulta;
