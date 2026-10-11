#!/usr/bin/env python3
"""Filtros reales de lectura, conteo/página consistentes y búsqueda literal sin SQL arbitrario."""
import json
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
secret=Path.home()/'.local/share/bovicierre-academic/secrets'
e='11111111-1111-4111-8111-111111111111';s='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';a='99999999-9999-4999-8999-999999999999'
with psycopg.connect(host='127.0.0.1',port=19999,dbname='bovicierre',user='bovi_app_a',password=(secret/'app_a_password').read_text().strip()) as con:
 def query(resource,params):return con.execute('select bovi.consultar(%s,%s,%s,%s,%s)',(e,s,a,resource,Jsonb(params))).fetchone()[0]
 first=query('animales',{'q':'DEMO-2026-10-V1','pagina':1,'tamano':1});second=query('animales',{'q':'DEMO-2026-10-V1','pagina':2,'tamano':1});assert first['total']==second['total']==3;assert first['elementos'][0]['id']!=second['elementos'][0]['id']
 operations=query('operaciones',{'q':'DEMO-2026-10-V1','estado':'CONFIRMADA','tipo':'COMPRA'});assert operations['total']==1 and operations['elementos'][0]['tipo']=='COMPRA'
 hostile=query('operaciones',{'q':"%' OR true --"});assert hostile['total']==0
 resources=['contrapartes','animales','operaciones','inventario_posiciones','pagos','liquidaciones','gastos','documentos','usuarios','periodos','reportes_cartera','reportes_margen']
 counts={resource:query(resource,{'q':'DEMO-2026-10-V1','pagina':1,'tamano':20})['total'] for resource in resources}
 con.execute('savepoint bad')
 try:query('operaciones',{'tipo':"COMPRA' OR true"})
 except psycopg.Error as ex:assert ex.sqlstate=='P0001';assert json.loads(ex.diag.message_detail)['campos'][0]['campo']=='tipo';con.execute('rollback to bad')
 else:raise AssertionError('Invalid typed filter accepted')
 Path('db/tests/filters-result.json').write_text(json.dumps({'counts':counts,'pagination_total3':True,'literal_search':True,'typed_filter_rejection':True},indent=2)+'\n')
 print('PASS V7 filters parameterized/literal, state+type, total/pagination, 12 UI resources')
