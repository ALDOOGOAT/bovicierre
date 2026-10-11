#!/usr/bin/env python3
"""TEST27: recreación sólo servicio pg-a del proyecto propio; firma datos/history/tokens antes/después."""
import hashlib,json,os,subprocess,time
from pathlib import Path
import psycopg
from psycopg import sql
sec=Path.home()/'.local/share/bovicierre-academic/secrets';name='bovicierre-academic-pg-a-1';st=time.monotonic()
def docker(*args):return subprocess.run(['docker',*args],capture_output=True,text=True,check=True).stdout.strip()
def inspect():return json.loads(docker('inspect',name))[0]
def ready():return subprocess.run(['docker','exec',name,'pg_isready','-U','postgres','-d','bovicierre'],capture_output=True).returncode==0
def wait():
 end=time.monotonic()+40
 while not ready():
  assert time.monotonic()<end;time.sleep(.1)
def connect(db):return psycopg.connect(host='127.0.0.1',port=15432,dbname=db,user='postgres',password=(sec/'admin_password').read_text().strip())
def fingerprint(db):
 with connect(db) as c:
  tables=c.execute("select schemaname,tablename from pg_tables where schemaname='bovi' or (schemaname='infra' and tablename not in ('spring_session','spring_session_attributes')) order by1,2".replace('order by1','order by 1')).fetchall();result={}
  for schema,table in tables:
   query=sql.SQL("select count(*),md5(coalesce(jsonb_agg(to_jsonb(t) order by to_jsonb(t)::text)::text,'[]')) from {}.{} t").format(sql.Identifier(schema),sql.Identifier(table));count,digest=c.execute(query).fetchone();result[schema+'.'+table]={'count':count,'md5':digest}
  return {'table_signatures':result,'signature_sha256':hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()}
old=inspect();assert old['Config']['Labels']['com.docker.compose.project']=='bovicierre-academic' and old['Config']['Labels']['com.docker.compose.service']=='pg-a';volume=next(x['Name'] for x in old['Mounts'] if x['Destination']=='/var/lib/postgresql');assert volume=='bovicierre-academic_pg-a'
# Wait for final QA facts to converge; historical local dedup/inbox aren't compared across nodes.
with connect('bovicierre_release_replay') as c:c.execute('select 1')
before={db:fingerprint(db) for db in ('bovicierre','bovicierre_release_replay')}
env=os.environ.copy();env['BOVI_SECRET_DIR']=str(sec)
try:
 outcome=subprocess.run(['docker','compose','-f','infra/compose/compose.academic.yml','up','-d','--no-deps','--force-recreate','pg-a'],env=env,capture_output=True,text=True,check=True);wait()
 new=inspect();assert old['Id']!=new['Id'];assert volume==next(x['Name'] for x in new['Mounts'] if x['Destination']=='/var/lib/postgresql');after={db:fingerprint(db) for db in before};assert before==after,'Persistence signature changed'
finally:
 docker('start',name);wait()
result={'seconds':round(time.monotonic()-st,3),'container_recreated':True,'old_container_id':old['Id'][:12],'new_container_id':new['Id'][:12],'same_named_volume':volume,'before':before,'after':after,'equal':True,'source_data_preserved':True,'excluded_only_ephemeral_auth_sessions':True};Path('db/tests/persistence-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS TEST27 '+json.dumps({k:v for k,v in result.items() if k not in ('before','after')}))
