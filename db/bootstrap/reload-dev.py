#!/usr/bin/env python3
"""Sólo reemplaza funciones/vistas de la infraestructura local de desarrollo."""
import re,subprocess,os
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sql=[]
for p in sorted((root/'db/migrations').glob('V[23]*')):
 text=p.read_text()
 for m in re.finditer(r'CREATE FUNCTION .*?\$\$;',text,re.S):sql.append(m[0].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1))
 for m in re.finditer(r'CREATE VIEW .*?;',text,re.S):sql.append(m[0].replace('CREATE VIEW','CREATE OR REPLACE VIEW',1))
sql.append(text[text.index('RESET ROLE;\nGRANT USAGE'):])
sql.append("DO $$ DECLARE r record; BEGIN FOR r IN SELECT p.oid::regprocedure fn,p.prosecdef FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='bovi' LOOP EXECUTE format('ALTER FUNCTION %s OWNER TO %I',r.fn,CASE WHEN r.prosecdef THEN 'bovi_command' ELSE 'bovi_owner' END); END LOOP; END $$; REVOKE ALL ON ALL FUNCTIONS IN SCHEMA bovi FROM PUBLIC; GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA bovi TO bovi_command;")
for node in 'ab':
 p=subprocess.run(['docker','exec','-i',f'bovicierre-academic-pg-{node}-1','psql','-q','-U','postgres','-d',os.environ.get('BOVI_DB_NAME','bovicierre'),'-v','ON_ERROR_STOP=1'],input='\n'.join(sql),text=True,capture_output=True)
 if p.returncode: raise RuntimeError(p.stderr)
print('Funciones/vistas actualizadas A/B (desarrollo)')
