DO $$ DECLARE n text; BEGIN
 FOR n IN SELECT unnest(ARRAY['bovi_owner','bovi_command','bovi_migrator','bovi_app_a','bovi_app_b','bovi_auditor','bovi_repl','bovi_monitor','bovi_backup','bovi_auth','bovi_worker']) LOOP
  IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=n) THEN EXECUTE format('CREATE ROLE %I %s',n,CASE WHEN n IN ('bovi_owner','bovi_command') THEN 'NOLOGIN' ELSE 'LOGIN' END); END IF;
 END LOOP;
END $$;
ALTER ROLE bovi_migrator NOINHERIT;
ALTER ROLE bovi_repl REPLICATION;
GRANT bovi_owner TO bovi_migrator;
GRANT pg_monitor TO bovi_monitor;
GRANT pg_read_all_data TO bovi_backup;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
