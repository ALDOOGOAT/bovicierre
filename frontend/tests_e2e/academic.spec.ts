import {test} from './runtime';
import {expect,type Page} from '@playwright/test';
import {readFile} from 'node:fs/promises';
import {homedir} from 'node:os';
// Cierre académico (§8.1, §8.2, §8.5): tablero de pendientes, guía de primer ingreso, selección paginada y restablecimiento.
const secret=()=>readFile(homedir()+'/.local/share/bovicierre-academic/secrets/demo_password','utf8').then(s=>s.trim());
const stamp=()=>Date.now().toString(36);
async function enter(page:Page,user:string,password:string){await page.goto('/');await page.getByLabel('Usuario *',{exact:true}).fill(user);await page.getByLabel('Contraseña *',{exact:true}).fill(password);await page.getByRole('button',{name:'Ingresar',exact:true}).click();}
async function login(page:Page){await enter(page,'demo.admin',await secret());await page.getByRole('button',{name:/DEMO Sede A/}).click();await expect(page.locator('#main-title')).toHaveText('Bandeja');}
async function nav(page:Page,hash:string){await page.goto('/'+new URL(page.url()).search+'#'+hash);await expect(page.locator('.loading')).toHaveCount(0);}
async function api(page:Page,suffix:string,body?:unknown,method='POST'){return page.evaluate(async({suffix,body,method})=>{const site=new URL(location.href).searchParams.get('sede');const csrf=await fetch('/api/v1/sesion/csrf').then(r=>r.json());const response=await fetch('/api/v1/sedes/'+site+suffix,{method,headers:{'Content-Type':'application/json',[csrf.headerName]:csrf.token,'Idempotency-Key':crypto.randomUUID()},...(body===undefined?{}:{body:JSON.stringify(body)})});const data=await response.json();if(!response.ok)throw new Error(JSON.stringify({status:response.status,data}));return {data};},{suffix,body,method});}

test('bandeja: pendientes con conteos del servidor y guía de primer ingreso',async({page})=>{
 await login(page);
 const board=page.getByRole('region',{name:'Pendientes de la sede'});await expect(board).toBeVisible();
 const card=(name:string)=>board.locator('[data-task="'+name+'"] strong');
 for(const name of ['Ganado por recibir','Entregas pendientes','Por cobrar','Por pagar','Sincronización'])await expect(card(name)).toHaveText(/^\d+$/);
 const reception=(await api(page,'/inventario/posiciones?estado=PENDIENTE_RECEPCION&pagina=1&tamano=1',undefined,'GET')).data.total;
 const receivable=(await api(page,'/reportes/cartera?direccion=POR_COBRAR&pagina=1&tamano=1',undefined,'GET')).data.total;
 await expect(card('Ganado por recibir')).toHaveText(String(reception));await expect(card('Por cobrar')).toHaveText(String(receivable));
 // La guía se muestra abierta la primera vez y queda cerrada al volver si la persona la cerró.
 const guide=page.locator('details.guide');await page.evaluate(()=>localStorage.removeItem('bovi.guia'));await page.reload();await expect(guide).toHaveAttribute('open','');
 await guide.locator('summary').click();await expect(guide).not.toHaveAttribute('open','');await page.reload();await expect(page.locator('details.guide')).not.toHaveAttribute('open','');
 await board.locator('[data-task="Por cobrar"]').click();await expect(page.locator('#main-title')).toHaveText('Cartera');
});

test('lote: selección más allá de la primera página sin perderla al paginar ni al buscar',async({page})=>{
 await login(page);const run=stamp();const party=(await api(page,'/contrapartes',{nombre:'DEMO PAGINA '+run,tipo_persona:'FISICA'})).data;
 // 51 identidades sintéticas con el mismo prefijo garantizan una segunda página (50 por página) sin depender de otros datos.
 for(let n=0;n<51;n++)await api(page,'/animales',{sexo:'M',identificaciones:[{sistema:'INTERNO',codigo:'DEMO-PAG-'+run+'-'+String(n).padStart(2,'0')}]});
 await api(page,'/animales',{sexo:'H',identificaciones:[{sistema:'INTERNO',codigo:'DEMO-EXTRA-'+run}]});
 const draft=(await api(page,'/operaciones',{tipo:'COMPRA',parte_id:party.id,fecha_operacion:'2026-10-11',requiere_recepcion:false})).data;
 await nav(page,'captura/'+draft.id);const status=page.getByRole('status').filter({hasText:'seleccionados'});
 await page.locator('[name="busqueda_ganado"]').fill('DEMO-PAG-'+run);await page.getByRole('button',{name:'Buscar ganado',exact:true}).click();
 const rows=page.locator('.selection-list label.check-row');const pager=page.locator('.selection-list + .pagination');
 await expect(rows).toHaveCount(50);await expect(pager).toContainText('51 registros · Página 1');
 await pager.getByRole('button',{name:'Siguiente',exact:true}).click();await expect(pager).toContainText('Página 2');await expect(rows).toHaveCount(1);
 const second=await rows.first().getAttribute('data-id');await rows.first().locator('input').check();await expect(status).toHaveText('1 seleccionados');
 await pager.getByRole('button',{name:'Anterior',exact:true}).click();await expect(rows).toHaveCount(50);await expect(status).toHaveText('1 seleccionados · 1 fuera de esta página o búsqueda');
 const first=await rows.first().getAttribute('data-id');await rows.first().locator('input').check();await expect(status).toHaveText('2 seleccionados · 1 fuera de esta página o búsqueda');
 await page.locator('[name="busqueda_ganado"]').fill('DEMO-EXTRA-'+run);await page.getByRole('button',{name:'Buscar ganado',exact:true}).click();await expect(rows).toHaveCount(1);
 await expect(status).toHaveText('2 seleccionados · 2 fuera de esta página o búsqueda');await expect(rows.first().locator('input')).not.toBeChecked();
 const extra=await rows.first().getAttribute('data-id');await rows.first().locator('input').check();await expect(status).toHaveText('3 seleccionados · 2 fuera de esta página o búsqueda');
 await page.locator('[name="precio_unitario"]').fill('10000');
 const saved=page.waitForResponse(r=>r.url().endsWith('/operaciones/'+draft.id)&&r.request().method()==='PATCH');await page.getByRole('button',{name:'Guardar condiciones del lote'}).click();expect((await saved).status()).toBeLessThan(300);
 const lot=(await api(page,'/operaciones/'+draft.id,undefined,'GET')).data.lotes[0];expect([...lot.animales].sort()).toEqual([first,second,extra].sort());
});

test('usuarios: restablecimiento administrativo de contraseña sin correo',async({page,browser})=>{
 await login(page);const run=stamp(),user='demo.reset.'+run,initial='Inicial-'+crypto.randomUUID(),reset='Nueva-'+crypto.randomUUID();
 const created=(await api(page,'/usuarios',{login:user,nombre:'DEMO restablecer '+run,contrasena:initial})).data;await api(page,'/usuarios/'+created.id+'/membresias',{rol_codigo:'AUDITOR',vigente:true});
 await nav(page,'usuarios');await page.locator('.list-filters [name="q"]').fill(user);await page.locator('.list-filters').getByRole('button',{name:'Buscar',exact:true}).click();await page.getByRole('row').filter({hasText:user}).getByRole('button',{name:/Abrir/}).click();
 const form=page.locator('form').filter({has:page.getByRole('button',{name:'Restablecer contraseña'})});
 await form.locator('[name="nueva_contrasena"]').fill(reset);await form.locator('[name="confirmar_contrasena"]').fill(reset+'x');await form.getByRole('button',{name:'Restablecer contraseña'}).click();await expect(form.getByRole('alert')).toContainText('no coinciden');
 await form.locator('[name="confirmar_contrasena"]').fill(reset);const patch=page.waitForResponse(r=>r.url().endsWith('/usuarios/'+created.id)&&r.request().method()==='PATCH');await form.getByRole('button',{name:'Restablecer contraseña'}).click();
 const response=await patch;expect(response.status()).toBe(200);expect(await response.json()).toMatchObject({contrasena_restablecida:true});expect(response.request().postData()).toContain('contrasena');
 await expect(form.getByRole('status')).toContainText('Contraseña restablecida');expect(await page.evaluate(()=>JSON.stringify(sessionStorage)+JSON.stringify(localStorage))).not.toContain(reset);
 const context=await browser.newContext({baseURL:new URL(page.url()).origin});const other=await context.newPage();
 try{await enter(other,user,initial);await expect(other.getByRole('alert')).toBeVisible();await enter(other,user,reset);await other.getByRole('button',{name:/DEMO Sede A/}).click();await expect(other.locator('#main-title')).toHaveText('Bandeja');}
 finally{await context.close();}
});

test('recorrido guiado y ayuda: diálogo accesible, fondo inerte, Escape devuelve el foco y videos servidos',async({page})=>{
 await login(page);await page.evaluate(()=>localStorage.setItem('bovi.tour.voz','off'));
 const launcher=page.getByRole('button',{name:'Recorrido guiado',exact:true});await launcher.click();
 const tour=page.getByRole('dialog',{name:'BoviCierre en dos minutos'});await expect(tour).toBeVisible();await expect(tour).toContainText('1 de 7');
 await expect(tour.getByRole('button',{name:'Siguiente'})).toBeFocused();await expect(page.locator('.app-shell > .workspace')).toHaveAttribute('inert','');
 const voice=tour.getByRole('button',{name:'Narración por voz'});await expect(voice).toHaveAttribute('aria-pressed','false');await voice.click();await expect(voice).toHaveAttribute('aria-pressed','true');await voice.click();await expect(voice).toHaveAttribute('aria-pressed','false');
 await tour.getByRole('button',{name:'Siguiente'}).click();await expect(page.getByRole('dialog',{name:'Lo pendiente de tu sede'})).toBeVisible();await expect(page.locator('.tour-spot')).toBeVisible();
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.locator('.app-shell > .workspace')).not.toHaveAttribute('inert','');await expect(launcher).toBeFocused();
 await nav(page,'ayuda');await expect(page.locator('#main-title')).toHaveText('Ayuda y tutoriales');
 const videos=page.locator('.video-card video');await expect(videos).toHaveCount(4);await expect(page.locator('.video-card track[kind="captions"][srclang="es"]')).toHaveCount(4);
 for(const src of await videos.locator('source').evaluateAll(els=>els.map(e=>(e as HTMLSourceElement).getAttribute('src')))){const r=await page.request.get(src!);expect(r.status(),src!).toBe(200);expect(r.headers()['content-type']).toContain('video/mp4');}
 for(const src of await page.locator('.video-card track').evaluateAll(els=>els.map(e=>(e as HTMLTrackElement).getAttribute('src')))){const r=await page.request.get(src!);expect(r.status(),src!).toBe(200);expect(await r.text()).toMatch(/^WEBVTT/);}
 await page.getByRole('button',{name:'Iniciar recorrido guiado'}).click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#main-title')).toHaveText('Bandeja');await page.getByRole('dialog').getByRole('button',{name:'Saltar'}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
});
