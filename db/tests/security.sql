\set ON_ERROR_STOP on
DO $$ DECLARE invalid integer; BEGIN
 SELECT count(*) INTO invalid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='bovi' AND p.prosecdef AND (r.rolname<>'bovi_command' OR p.proconfig IS DISTINCT FROM ARRAY['search_path=pg_catalog, pg_temp']);
 ASSERT invalid=0,'Security-definer owner/search_path mismatch';
 -- SF-08 (V14): toda función con search_path fijo termina en pg_temp; PUBLIC sin TEMP.
 SELECT count(*) INTO invalid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname IN ('bovi','infra') AND p.proconfig IS DISTINCT FROM ARRAY['search_path=pg_catalog, pg_temp'];
 ASSERT invalid=0,'Function without pg_catalog, pg_temp search_path';
 ASSERT NOT EXISTS(SELECT 1 FROM pg_database d, aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) x WHERE d.datname=current_database() AND x.grantee=0 AND x.privilege_type='TEMPORARY'),'PUBLIC can create temp tables';
 ASSERT NOT has_database_privilege('bovi_app_a',current_database(),'TEMP') AND NOT has_database_privilege('bovi_auditor',current_database(),'TEMP'),'Runtime role can create temp tables';
 SELECT count(*) INTO invalid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='bovi' AND EXISTS(SELECT 1 FROM aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) WHERE grantee=0 AND privilege_type='EXECUTE');
 ASSERT invalid=0,'PUBLIC function execution permitted';
 ASSERT NOT has_table_privilege('bovi_app_a','bovi.liquidacion','UPDATE'),'Runtime can alter settlement';
 ASSERT NOT has_table_privilege('bovi_app_b','bovi.posicion_inventario','INSERT'),'Runtime can manufacture inventory';
 ASSERT NOT has_table_privilege('bovi_app_a','infra.nodo_config','UPDATE'),'Runtime can change fixed deployment scope';
 ASSERT NOT has_table_privilege('bovi_auth','bovi.operacion','INSERT'),'Auth role has financial writes';
 ASSERT NOT has_table_privilege('bovi_worker','bovi.animal','UPDATE'),'Worker bypasses master command';
 ASSERT NOT has_column_privilege('bovi_app_a','bovi.usuario','hash_contrasena','SELECT'),'Business role reads password hashes';
 ASSERT NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('bovi_app_a','bovi_app_b','bovi_auth','bovi_worker') AND (rolsuper OR rolbypassrls OR rolreplication)),'Runtime elevated attributes';
END $$;
SELECT 'PASS SECURITY DEFINER ACLs/safe path/runtime roles' AS resultado;
SET ROLE bovi_auditor;
DO $$ DECLARE denied boolean:=false; BEGIN
 BEGIN UPDATE bovi.liquidacion SET total=total WHERE false; EXCEPTION WHEN insufficient_privilege THEN denied:=true; END;
 ASSERT denied,'Auditor can alter economic facts';
END $$;
RESET ROLE;
SELECT 'PASS auditor role protected DML42501' AS resultado;
SET ROLE bovi_auditor;
DO $$ DECLARE denied boolean:=false; BEGIN
 BEGIN CREATE TEMP TABLE pg_tables(x int); EXCEPTION WHEN insufficient_privilege THEN denied:=true; END;
 ASSERT denied,'Runtime role can shadow catalog with pg_temp';
END $$;
RESET ROLE;
SELECT 'PASS pg_temp shadowing denied (SF-08)' AS resultado;


-- Negative trigger checks as the function owner; independent from runtime DML denial.
SET ROLE bovi_command;
DO $$ DECLARE c record; blocked boolean; BEGIN
 SELECT * INTO c FROM bovi.contrato_version WHERE estado='ACEPTADA' LIMIT 1;
 IF FOUND THEN
  blocked:=false;
  BEGIN UPDATE bovi.contrato_version SET estado=estado WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_version); EXCEPTION WHEN SQLSTATE 'P0001' THEN blocked:=true; END;
  ASSERT blocked,'Accepted contract trigger failed';
  blocked:=false;
  BEGIN UPDATE bovi.condicion_lote SET precio_unitario=precio_unitario WHERE (empresa_id,sucursal_id,operacion_id,numero_version)=(c.empresa_id,c.sucursal_id,c.operacion_id,c.numero_version); EXCEPTION WHEN SQLSTATE 'P0001' THEN blocked:=true; END;
  ASSERT blocked,'Accepted condition trigger failed';
 END IF;
END $$;
RESET ROLE;
SELECT 'PASS immutable accepted contract/condition triggers (definer-owner DML)' AS resultado;
