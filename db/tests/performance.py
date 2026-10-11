#!/usr/bin/env python3
"""Muestras de lectura pequeña local; no SLO, capacidad ni carga concurrente de producción."""
import json,math,os,statistics,time
from pathlib import Path
import psycopg
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';secret=Path.home()/'.local/share/bovicierre-academic/secrets'
e='11111111-1111-4111-8111-111111111111';s='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
queries={'inventario':"SELECT * FROM bovi.posicion_inventario WHERE empresa_id=%s AND sucursal_id=%s AND estado='DISPONIBLE'",'cartera':'SELECT * FROM bovi.v_saldo_liquidacion WHERE empresa_id=%s AND sucursal_id=%s','liquidacion':'SELECT * FROM bovi.concepto_liquidacion WHERE empresa_id=%s AND sucursal_id=%s','expediente':'SELECT * FROM bovi.movimiento_inventario WHERE empresa_id=%s AND sucursal_id=%s'}
result={'database':DB,'conexion':'PostgreSQL directo15432, conexión única reutilizada','samples_per_query':100,'warmup_per_query':5,'concurrency':1,'scope':'Fixture DEMO pequeño; caché caliente y sin carga. No acredita SLO ni capacidad producción.','dataset':{},'queries':{}}
with psycopg.connect(host='127.0.0.1',port=15432,dbname=DB,user='bovi_app_a',password=(secret/'app_a_password').read_text().strip()) as con:
 for table in ['animal','operacion','posicion_inventario','liquidacion','concepto_liquidacion','movimiento_inventario']:
  result['dataset'][table]=con.execute('SELECT count(*) FROM bovi.'+table).fetchone()[0]
 for name,sql in queries.items():
  for _ in range(5):con.execute(sql,(e,s)).fetchall()
  samples=[]
  for _ in range(100):
   start=time.perf_counter_ns();rows=con.execute(sql,(e,s)).fetchall();samples.append((time.perf_counter_ns()-start)/1e6)
  plan=con.execute('EXPLAIN(ANALYZE,BUFFERS,FORMAT JSON) '+sql,(e,s)).fetchone()[0][0]
  result['queries'][name]={'rows':len(rows),'p50_ms':round(statistics.median(samples),3),'p95_ms':round(sorted(samples)[math.ceil(.95*len(samples))-1],3),'explain':plan}
Path('db/tests/performance-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS 4 query plans +100samples each; observations only '+json.dumps({k:{f:v[f] for f in ['p50_ms','p95_ms']} for k,v in result['queries'].items()}))
