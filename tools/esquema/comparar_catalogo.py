#!/usr/bin/env python3
"""Contrasta columnas, tipos, nullabilidad, PK, UK declaradas y FK lógicas contra PostgreSQL propio."""
import argparse
import json
import subprocess
from esquema import TABLAS

SQL = """
SELECT jsonb_build_object(
 'columns', (SELECT jsonb_agg(jsonb_build_object('schema',n.nspname,'table',c.relname,'name',a.attname,'not_null',a.attnotnull,'type',format_type(a.atttypid,a.atttypmod)))
 FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname IN ('bovi','infra') AND c.relkind IN ('r','p') AND a.attnum>0 AND NOT a.attisdropped),
 'keys', (SELECT jsonb_agg(jsonb_build_object('table',c.relname,'schema',n.nspname,'kind',k.contype,
 'columns', ARRAY(SELECT a.attname FROM unnest(k.conkey) WITH ORDINALITY q(num,ord) JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=q.num ORDER BY q.ord),
 'target',r.relname,'target_schema',rn.nspname,
 'target_columns', ARRAY(SELECT a.attname FROM unnest(k.confkey) WITH ORDINALITY q(num,ord) JOIN pg_attribute a ON a.attrelid=r.oid AND a.attnum=q.num ORDER BY q.ord)))
 FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
 LEFT JOIN pg_class r ON r.oid=k.confrelid LEFT JOIN pg_namespace rn ON rn.oid=r.relnamespace
 WHERE n.nspname IN ('bovi','infra') AND k.contype IN ('p','f','u')));
"""


def qualified(name):
    return name if '.' in name else 'bovi.' + name


def normalize_type(value):
    value = value.replace(' GEN', '').lower()
    return value.replace('character varying', 'varchar').replace('character(', 'char(').replace('timestamp with time zone', 'timestamptz').replace(' ', '')


def compare(tables, catalog):
    actual_columns = {}
    for column in catalog['columns'] or []:
        table = column['schema'] + '.' + column['table']
        actual_columns.setdefault(table, {})[column['name']] = (column['not_null'], normalize_type(column.get('type', '')))
    actual_keys = {}
    for key in catalog['keys'] or []:
        actual_keys.setdefault(key['schema'] + '.' + key['table'], []).append(key)
    errors = []
    for _, name, columns, foreign_keys, unique_keys in tables:
        table = qualified(name)
        expected = {name: ('NN' in flags, normalize_type(kind)) for name, kind, flags in columns}
        actual = actual_columns.get(table, {})
        for name in sorted(expected.keys() | actual.keys()):
            if expected.get(name) != actual.get(name) or name not in expected or name not in actual:
                errors.append(f'{table}.{name}: tipo/nullabilidad/presencia lógica={expected.get(name)} física={actual.get(name)}')
        keys = actual_keys.get(table, [])
        primary = [column for column, _, flags in columns if 'PK' in flags]
        if not any(key['kind'] == 'p' and key['columns'] == primary for key in keys):
            errors.append(f'{table}: PK no concuerda {primary}')
        for unique in unique_keys:
            if not any(key['kind'] in ('u', 'p') and key['columns'] == list(unique) for key in keys):
                errors.append(f'{table}: UK declarada ausente {unique}')
        expected_fks = {(tuple(local), qualified(target), tuple(remote)) for local, target, remote in foreign_keys}
        actual_fks = {(tuple(key['columns']), key['target_schema'] + '.' + key['target'], tuple(key['target_columns'])) for key in keys if key['kind'] == 'f'}
        for key in sorted(expected_fks - actual_fks):
            errors.append(f'{table}: FK lógica ausente {key}')
        for key in sorted(actual_fks - expected_fks):
            errors.append(f'{table}: FK física sin metadata {key}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='bovicierre-academic-pg-a-1')
    parser.add_argument('--project', default='bovicierre-academic')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        table = [('test', 'child', [('id','uuid',{'PK','NN'}),('parent_id','uuid',{'NN'})], [(['parent_id'],'parent',['id'])], [])]
        catalog = {'columns':[{'schema':'bovi','table':'child','name':name,'not_null':True,'type':'uuid'} for name in ('id','parent_id')], 'keys':[{'schema':'bovi','table':'child','kind':'p','columns':['id']}]}
        assert len(compare(table,catalog)) == 1 and 'FK lógica ausente' in compare(table,catalog)[0]
        assert normalize_type('character varying(20)') == 'varchar(20)'
        assert normalize_type('numeric(18,2) GEN') == 'numeric(18,2)'
        catalog['columns'][0]['type'] = 'text'
        assert any('tipo/nullabilidad' in error for error in compare(table, catalog))
        print('comparar_catalogo self-check OK')
        return 0
    labels = json.loads(subprocess.check_output(['docker','inspect','--format','{{json .Config.Labels}}',args.container],text=True))
    if not args.project.startswith('bovicierre-') or labels.get('com.docker.compose.project') != args.project:
        raise SystemExit('Contenedor no pertenece al proyecto BoviCierre indicado; no se consulta.')
    raw = subprocess.check_output(['docker','exec','-i',args.container,'psql','-U','postgres','-d','bovicierre','-X','-At','-v','ON_ERROR_STOP=1'],input=SQL,text=True)
    errors = compare(TABLAS,json.loads(raw))
    print(json.dumps({'tables_checked':len(TABLAS),'errors':errors,'scope':'Columnas/tipos/nullabilidad/PK/UK declaradas/FK; no demuestra CHECK, privilegios, índices parciales ni todas las RN.'},ensure_ascii=False,indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
