#!/usr/bin/env python3
"""Bootstrap aislado, repetible; nunca opera contenedores fuera de bovicierre-academic."""
import os, subprocess, time, sys, re
if os.environ.get('BOVI_ENV','').strip().lower()=='production' or 'production' in {profile.strip().lower() for profile in os.environ.get('SPRING_PROFILES_ACTIVE','').split(',')}:
 raise SystemExit('Entorno production: bootstrap/semilla DEMO bloqueados antes de cualquier operación.')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SECRET=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'))
PROJECT=os.environ.get('BOVI_COMPOSE_PROJECT','bovicierre-academic')
DATABASE=os.environ.get('BOVI_DB_NAME','bovicierre')
if not re.fullmatch(r'bovicierre-[a-z0-9-]+',PROJECT) or not re.fullmatch(r'[a-z][a-z0-9_]*',DATABASE): raise ValueError('Nombre de proyecto/base aislados inválido')
E='11111111-1111-4111-8111-111111111111'; A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'; B='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'; U='99999999-9999-4999-8999-999999999999'
# BOVI_INSTALL=vacia: empresa, sedes y primer administrador propios (UUID generados y persistidos fuera del repo),
# sin usuarios ni datos DEMO. La semilla DEMO (make demo) exige la empresa DEMO y por eso no corre aquí.
INSTALL=os.environ.get('BOVI_INSTALL','demo').strip().lower()
if INSTALL not in ('demo','vacia'): raise SystemExit('BOVI_INSTALL debe ser demo o vacia')
if INSTALL=='vacia':
 import json,uuid,secrets as tokens
 install=Path(os.environ.get('BOVI_INSTALL_FILE',SECRET.parent/'install.json'))
 if install.exists(): cfg=json.loads(install.read_text())
 else:
  cfg={'modo':'vacia','empresa':str(uuid.uuid4()),'empresa_nombre':os.environ.get('BOVI_EMPRESA','').strip(),'sede_a':str(uuid.uuid4()),'sede_a_nombre':os.environ.get('BOVI_SEDE_A','Sede principal').strip(),
       'sede_b':str(uuid.uuid4()),'sede_b_nombre':os.environ.get('BOVI_SEDE_B','Sede secundaria').strip(),'admin':str(uuid.uuid4()),'admin_login':os.environ.get('BOVI_ADMIN_LOGIN','admin').strip().lower()}
  if not cfg['empresa_nombre'] or cfg['empresa_nombre'].upper().startswith('DEMO'): raise SystemExit('Instalación vacía: indica BOVI_EMPRESA (razón social real o de prueba, sin prefijo DEMO).')
  if not cfg['sede_a_nombre'] or not cfg['sede_b_nombre'] or not re.fullmatch(r'[a-z][a-z0-9._-]{2,79}',cfg['admin_login']): raise SystemExit('Instalación vacía: nombres de sede y BOVI_ADMIN_LOGIN (3-80, minúsculas) obligatorios.')
  install.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  with os.fdopen(os.open(install,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as out: json.dump(cfg,out,ensure_ascii=False,indent=1)
 if cfg.get('modo')!='vacia': raise SystemExit('Archivo de instalación inesperado: '+str(install))
 E,A,B,U=cfg['empresa'],cfg['sede_a'],cfg['sede_b'],cfg['admin']
 first=SECRET/'install_admin_password'
 if not first.exists():
  with os.fdopen(os.open(first,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as out: out.write(tokens.token_urlsafe(18)+'\n')
def lit(v): return "'"+str(v).replace("'","''")+"'"
# Destino remoto opcional (p. ej. Railway): BOVI_PSQL_TARGETS='{"a":"host:puerto","b":…,"prov":…}' usa psql por TCP
# con la contraseña de administrador; BOVI_INTERNAL_SUFFIX ('.railway.internal') completa los nombres de la red privada.
import json as _json
TARGETS=_json.loads(os.environ.get('BOVI_PSQL_TARGETS','{}'))
SUFFIX=os.environ.get('BOVI_INTERNAL_SUFFIX','')
def internal(node): return 'pg-'+node+SUFFIX
def sql(node, query):
 if TARGETS:
  host,port=TARGETS[node].rsplit(':',1)
  p=subprocess.run(['psql','-X','-qAt','-h',host,'-p',port,'-U','postgres','-d',DATABASE,'-v','ON_ERROR_STOP=1'],input=query,text=True,capture_output=True,env={**os.environ,'PGPASSWORD':secret('admin_password'),'PGSSLMODE':os.environ.get('BOVI_PG_SSLMODE','require')})
 else:
  p=subprocess.run(['docker','exec','-i',f'{PROJECT}-pg-{node}-1','psql','-X','-qAt','-U','postgres','-d',DATABASE,'-v','ON_ERROR_STOP=1'],input=query,text=True,capture_output=True)
 if p.returncode:
  error=p.stderr
  for file in SECRET.iterdir():
   if file.is_file(): error=error.replace(file.read_text().strip(),'[REDACTADO]')
  raise RuntimeError(error)
 return p.stdout.strip()
def secret(n): return (SECRET/n).read_text().strip()
if sql('a','SELECT count(*) FROM bovi.empresa WHERE id<>'+lit(E)+'::uuid')!='0': raise SystemExit('La base ya contiene otra empresa: la instalación '+INSTALL+' requiere una base o volúmenes nuevos.')
for node in 'ab':
 sql(node,"INSERT INTO infra.nodo_config VALUES("+lit(node.upper())+','+lit(E)+','+lit('Instalación vacía' if INSTALL=='vacia' else 'DEMO despliegue aislado')+") ON CONFLICT DO NOTHING;")
 for role,file in [('bovi_app_a','app_a_password'),('bovi_app_b','app_b_password'),('bovi_auth','auth_password'),('bovi_worker','worker_password'),('bovi_repl','repl_password')]: sql(node,f'ALTER ROLE {role} PASSWORD {lit(secret(file))};')
masters=['empresa','sucursal','rol_aplicacion','usuario','membresia_usuario','parte','predio','animal','animal_identificacion']
local=sql('a',"SELECT tablename FROM pg_tables WHERE schemaname='bovi' AND tablename NOT IN ('empresa','sucursal','rol_aplicacion','usuario','membresia_usuario','parte','predio','animal','animal_identificacion','clave_idempotencia','mensaje_inbox') ORDER BY tablename;").splitlines()
restore_converged=os.environ.get('BOVI_RESTORE_CONVERGED')=='1'
if restore_converged:
 for table in masters+local:
  query="SELECT count(*)::text||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'' ORDER BY md5(to_jsonb(t)::text))),md5('')) FROM bovi."+table+' t'
  if sql('a',query)!=sql('b',query):raise RuntimeError('Restauración no convergente; publicación bloqueada: '+table)
for node in 'ab':
 pub='pub_'+node
 if sql(node,f"SELECT count(*) FROM pg_publication WHERE pubname='{pub}'")=='0':
  if not restore_converged and any(sql(node,'SELECT count(*) FROM bovi.'+t)!='0' for t in ((masters+local) if node=='a' else local)): raise RuntimeError('Bootstrap origin=none/copy_data=false exige fuentes vacías o suscripciones existentes')
  sql(node,'CREATE PUBLICATION '+pub+' FOR TABLE '+','.join('bovi.'+t for t in ((masters+local) if node=='a' else local))+';')
for node,remote in [('b','a'),('a','b')]:
 sub=f'sub_{node}_desde_{remote}'
 if sql(node,f"SELECT count(*) FROM pg_subscription WHERE subname='{sub}' AND subdbid=(SELECT oid FROM pg_database WHERE datname=current_database())")=='0':
  connection=f'host={internal(remote)} port=5432 dbname={DATABASE} user=bovi_repl password={secret("repl_password")} connect_timeout=3'
  slot_suffix='' if DATABASE=='bovicierre' else '_'+DATABASE
  sql(node,f'CREATE SUBSCRIPTION {sub} CONNECTION {lit(connection)} PUBLICATION pub_{remote} WITH(slot_name=\'slot_{remote}_para_{node}{slot_suffix}\',origin=none,copy_data=false);')
if INSTALL=='vacia':
 sql('a',f"""INSERT INTO bovi.empresa VALUES('{E}',{lit(cfg['empresa_nombre'])},NULL,'ACTIVA','A',now()) ON CONFLICT DO NOTHING;
INSERT INTO bovi.sucursal VALUES('{E}','{A}','SEDE-A',{lit(cfg['sede_a_nombre'])},'A','America/Mexico_City','A'),('{E}','{B}','SEDE-B',{lit(cfg['sede_b_nombre'])},'B','America/Mexico_City','A') ON CONFLICT DO NOTHING;
INSERT INTO bovi.rol_aplicacion VALUES('ADMIN','Administración'),('OPERADOR','Operación'),('CAJA','Caja'),('AUDITOR','Consulta') ON CONFLICT DO NOTHING;
INSERT INTO bovi.usuario VALUES('{E}','{U}',{lit(cfg['admin_login'])},'Primer administrador','{{bcrypt}}'||public.crypt({lit(secret('install_admin_password'))},public.gen_salt('bf',10)),'ACTIVO','A',now()) ON CONFLICT DO NOTHING;
INSERT INTO bovi.membresia_usuario VALUES('{E}','{A}','{U}','ADMIN',true,'A'),('{E}','{B}','{U}','ADMIN',true,'A') ON CONFLICT DO NOTHING;""")
else:
 seed=f"""
INSERT INTO bovi.empresa VALUES('{E}','DEMO BoviCierre académico',NULL,'ACTIVA','A',now()) ON CONFLICT DO NOTHING;
INSERT INTO bovi.sucursal VALUES('{E}','{A}','DEMO-A','DEMO Sede A','A','America/Mexico_City','A'),('{E}','{B}','DEMO-B','DEMO Sede B','B','America/Mexico_City','A') ON CONFLICT DO NOTHING;
INSERT INTO bovi.rol_aplicacion VALUES('ADMIN','DEMO administración'),('OPERADOR','Operación'),('CAJA','Caja'),('AUDITOR','Consulta') ON CONFLICT DO NOTHING;
INSERT INTO bovi.usuario VALUES('{E}','{U}','demo.admin','DEMO administrador','{{bcrypt}}'||public.crypt({lit(secret('demo_password'))},public.gen_salt('bf',10)),'ACTIVO','A',now()) ON CONFLICT DO NOTHING;
INSERT INTO bovi.membresia_usuario VALUES('{E}','{A}','{U}','ADMIN',true,'A'),('{E}','{B}','{U}','ADMIN',true,'A') ON CONFLICT DO NOTHING;
"""
 sql('a',seed)
 for code,role,num in [('operador','OPERADOR',8),('caja','CAJA',7),('auditor','AUDITOR',6)]:
  uid=f'{num}9999999-9999-4999-8999-999999999999'
  password=secret(f'demo_{code}_password')
  sql('a',f"INSERT INTO bovi.usuario VALUES('{E}','{uid}','demo.{code}','DEMO {code}','{{bcrypt}}'||public.crypt({lit(password)},public.gen_salt('bf',10)),'ACTIVO','A',now()) ON CONFLICT DO NOTHING; INSERT INTO bovi.membresia_usuario VALUES('{E}','{A}','{uid}','{role}',true,'A'),('{E}','{B}','{uid}','{role}',true,'A') ON CONFLICT DO NOTHING;")
for _ in range(100):
 if sql('b',f"SELECT count(*) FROM bovi.membresia_usuario WHERE usuario_id='{U}'")=='2': break
 time.sleep(.2)
else: raise RuntimeError('Maestros no convergieron; no habilitar B')
provider=f"""CREATE SCHEMA IF NOT EXISTS proveedor; DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='bovi_fdw_read') THEN CREATE ROLE bovi_fdw_read LOGIN; END IF; END $$; ALTER ROLE bovi_fdw_read PASSWORD {lit(secret('fdw_password'))};
CREATE TABLE IF NOT EXISTS proveedor.tarifa_transporte(ruta text PRIMARY KEY,origen text,destino text,precio_mxn numeric(14,4),unidad text,vigente_desde date,version integer);
CREATE TABLE IF NOT EXISTS proveedor.ticket_bascula(folio text PRIMARY KEY,bascula text,pesado_en timestamptz,neto_kg numeric(14,3),nota text);
INSERT INTO proveedor.tarifa_transporte VALUES('DEMO-RUTA-01','DEMO origen','DEMO destino',12000,'VIAJE',current_date,1) ON CONFLICT DO NOTHING;
INSERT INTO proveedor.ticket_bascula VALUES('DEMO-TICKET-01','DEMO báscula',now(),5000,'Datos sintéticos') ON CONFLICT DO NOTHING;
REVOKE ALL ON SCHEMA public FROM PUBLIC; GRANT USAGE ON SCHEMA proveedor TO bovi_fdw_read; GRANT SELECT ON ALL TABLES IN SCHEMA proveedor TO bovi_fdw_read;"""
sql('prov',provider)
fdw=f"""CREATE EXTENSION IF NOT EXISTS postgres_fdw; CREATE SCHEMA IF NOT EXISTS ext_proveedor; DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_foreign_server WHERE srvname='prov_sim') THEN CREATE SERVER prov_sim FOREIGN DATA WRAPPER postgres_fdw OPTIONS(host '{internal("prov")}',dbname '{DATABASE}',connect_timeout '3'); END IF; END $$;
"""
# FDW desde ambos maestros hacia la tercera instancia (la “Y” del pizarrón): A y B leen el proveedor, nunca escriben.
for node in 'ab':
 sql(node,fdw)
 # IMPORT uses bootstrap identity; definer and business roles have SELECT-only provider mapping.
 for role in ['postgres','bovi_command','bovi_app_'+node]:
  sql(node,f"CREATE USER MAPPING IF NOT EXISTS FOR {role} SERVER prov_sim OPTIONS(user 'bovi_fdw_read',password {lit(secret('fdw_password'))});")
 if sql(node,"SELECT count(*) FROM information_schema.foreign_tables WHERE foreign_table_schema='ext_proveedor'")=='0': sql(node,'IMPORT FOREIGN SCHEMA proveedor LIMIT TO(tarifa_transporte,ticket_bascula) FROM SERVER prov_sim INTO ext_proveedor;')
 sql(node,'GRANT USAGE ON SCHEMA ext_proveedor TO bovi_command,bovi_app_'+node+'; GRANT SELECT ON ALL TABLES IN SCHEMA ext_proveedor TO bovi_command,bovi_app_'+node+';')
print('Bootstrap: A/B PostgreSQL18, maestros convergentes, proveedor FDW SELECT-only desde A y B preparado.')
