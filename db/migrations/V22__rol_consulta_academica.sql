-- V22: rol de grupo para cuentas personales de consulta (profesor y equipo), sin contraseña en la migración.
-- Hereda la lectura de bovi_auditor (todas las tablas de bovi salvo el hash de contraseña) y pg_monitor para
-- inspeccionar réplica (pg_stat_replication, pg_stat_subscription) y actividad. No escribe ni ejecuta comandos.
-- Las cuentas LOGIN se crean con scripts/academic_users.py y sus contraseñas viven fuera del repositorio.
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='bovi_consulta') THEN CREATE ROLE bovi_consulta NOLOGIN; END IF;
END $$;
GRANT bovi_auditor TO bovi_consulta;
GRANT pg_monitor TO bovi_consulta;
