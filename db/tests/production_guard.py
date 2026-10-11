#!/usr/bin/env python3
"""Guarda producción antes de dependencias, archivos secretos, Docker o BD; sin servicios."""
import json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];results=[]
for script in ('db/bootstrap/bootstrap.py','db/seed/demo.py'):
 for case in ({'BOVI_ENV':'production'},{'SPRING_PROFILES_ACTIVE':'production'},{'SPRING_PROFILES_ACTIVE':'dev, Production '}):
  env=dict(os.environ);env.pop('BOVI_ENV',None);env.pop('SPRING_PROFILES_ACTIVE',None);env.update(case);env['PATH']='/nonexistent';env['BOVI_SECRET_DIR']='/nonexistent/bovicierre-secret';env['BOVI_COMPOSE_PROJECT']='invalid-before-guard'
  child=subprocess.run([sys.executable,str(root/script)],env=env,capture_output=True,text=True,timeout=5)
  assert child.returncode==1 and child.stdout=='' and child.stderr.strip()=='Entorno production: bootstrap/semilla DEMO bloqueados antes de cualquier operación.',(script,child.returncode,child.stderr)
  results.append({'script':script,'variable':next(iter(case)),'exit_code':child.returncode,'reject_before_Docker_DB_secret_read':True})
report={'cases':results,'total':len(results),'services_operated':False,'database_access':False};(root/'db/tests/production-guard-result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS production guard '+json.dumps(report))
