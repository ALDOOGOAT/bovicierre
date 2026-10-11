#!/usr/bin/env python3
"""Compara catálogo real contra replay limpio; adopta baseline3 sin simular ejecución histórica."""
import json,os,subprocess,re
from pathlib import Path
import psycopg
ROOT=Path(__file__).resolve().parents[2]
SECRET=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'))
REPLAY=os.environ.get('BOVI_REPLAY_DB','bovicierre_final_replay')
QUERIES={
 'columnas':"SELECT n.nspname,c.relname,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull,pg_get_expr(d.adbin,d.adrelid),a.attgenerated FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum WHERE n.nspname IN ('bovi','infra') AND c.relkind IN ('r','v') AND c.relname<>'flyway_schema_history' AND a.attnum>0 AND NOT a.attisdropped ORDER BY 1,2,3",
 'restricciones':"SELECT n.nspname,c.relname,k.contype::text,pg_get_constraintdef(k.oid) FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('bovi','infra') AND c.relname<>'flyway_schema_history' ORDER BY 1,2,3,4",
 'indices':"SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes WHERE schemaname IN ('bovi','infra') AND tablename<>'flyway_schema_history' ORDER BY 1,2,3",
 'funciones':"SELECT p.oid::regprocedure::text,p.prosrc,p.prosecdef,p.proconfig,r.rolname,array(SELECT x::text FROM unnest(p.proacl) x ORDER BY x::text) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='bovi' ORDER BY 1",
 'triggers':"SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='bovi' AND NOT t.tgisinternal ORDER BY 1,2",
 'vistas':"SELECT viewname,definition FROM pg_views WHERE schemaname='bovi' ORDER BY 1",
 'permisos':"SELECT n.nspname,c.relname,r.rolname,array(SELECT x::text FROM unnest(c.relacl) x ORDER BY x::text) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname IN ('bovi','infra') AND c.relkind IN ('r','v') AND c.relname<>'flyway_schema_history' ORDER BY 1,2",
}
def catalog(db,port):
 with psycopg.connect(host='127.0.0.1',port=port,dbname=db,user='postgres',password=(SECRET/'admin_password').read_text().strip()) as c:
  result={k:c.execute(v).fetchall() for k,v in QUERIES.items()}
  # SELECT p.* expands in physical column order; JSON uses names. Preserve expression semantics.
  result['vistas']=[(name,re.sub(r'^( SELECT )(?:[a-z_]+,\n    )+',lambda m:' SELECT '+','.join(sorted(re.findall(r'[a-z_]+',m[0])[1:]))+', ',definition)) for name,definition in result['vistas']]
  return result
result={'replay':REPLAY,'declaracion':'Baseline3 adopta catálogo existente; V1/V2/V3 no se afirman ejecutadas originalmente por Flyway.','normalizacion':'CHECK compara expresión/tipo sin nombre autogenerado; vistas normalizan orden físico de columnas simples de SELECT *. Tipos, nulabilidad, defaults, índices, FK, funciones, ACL, triggers y expresiones se comparan.','nodos':{},'aprobado':True}
for node,port in [('A',15432),('B',15433)]:
 existing=catalog('bovicierre',port); replay=catalog(REPLAY,port)
 diffs={k:{'existente_solo':[r for r in existing[k] if r not in replay[k]],'replay_solo':[r for r in replay[k] if r not in existing[k]]} for k in QUERIES if existing[k]!=replay[k]}
 result['nodos'][node]={'conteos':{k:len(existing[k]) for k in QUERIES},'diferencias':diffs};result['aprobado'] &= not diffs
out=ROOT/'db/tests/flyway-adoption.json';out.write_text(json.dumps(result,indent=2,default=str)+'\n')
if not result['aprobado']:raise SystemExit('Catálogo difiere; baseline bloqueado. Consulte db/tests/flyway-adoption.json')
if os.environ.get('BOVI_ADOPT_BASELINE')=='1':
 subprocess.run(['mvn','-q','-f',str(ROOT/'db/migrate/pom.xml'),'package','dependency:copy-dependencies'],check=True)
 for port in (15432,15433):subprocess.run(['java','-cp',str(ROOT/'db/migrate/target/classes')+':'+str(ROOT/'db/migrate/target/dependency/*'),'mx.bovicierre.Migrate',f'jdbc:postgresql://127.0.0.1:{port}/bovicierre',str(SECRET/'admin_password'),str(ROOT/'db/migrations'),'baseline3'],check=True)
print('PASS comparación completa A/B; '+('baseline3 adoptado' if os.environ.get('BOVI_ADOPT_BASELINE')=='1' else 'sin adopción (sólo comparación)'))
