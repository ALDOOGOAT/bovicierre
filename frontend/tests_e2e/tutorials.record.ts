import {test,expect,type BrowserContext,type Locator,type Page} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {mkdir,readFile,unlink,writeFile} from 'node:fs/promises';
import {homedir} from 'node:os';
import {resolve} from 'node:path';
// Videos de uso con subtítulos WebVTT sincronizados: cada subtítulo se registra en el instante real del paso grabado.
// Datos sintéticos DEMO creados por la API antes de grabar. Salida: public/videos/<id>.mp4|.vtt|-poster.jpg.
test.describe.configure({mode:'serial'});
const OUT=resolve('public/videos');const run=Date.now().toString(36);const party='DEMO Rancho Video '+run;
const shared:{context?:BrowserContext;search?:string;purchase?:string;sale?:string;animals:string[]}={animals:[]};
const password=()=>readFile(homedir()+'/.local/share/bovicierre-academic/secrets/demo_password','utf8').then(v=>v.trim());
const CURSOR=`addEventListener('DOMContentLoaded',()=>{const c=document.createElement('div');c.setAttribute('aria-hidden','true');Object.assign(c.style,{position:'fixed',left:'-40px',top:'-40px',width:'22px',height:'22px',margin:'-11px 0 0 -11px',borderRadius:'50%',background:'rgba(201,162,74,.55)',border:'2px solid #fff',boxShadow:'0 2px 10px rgba(0,0,0,.35)',zIndex:'2147483647',pointerEvents:'none',transition:'transform .12s'});document.body.appendChild(c);addEventListener('mousemove',e=>{c.style.left=e.clientX+'px';c.style.top=e.clientY+'px';},true);addEventListener('mousedown',()=>{c.style.transform='scale(.65)';},true);addEventListener('mouseup',()=>{c.style.transform='';},true);});`;

async function api(page:Page,suffix:string,body?:unknown,method='POST'){return page.evaluate(async({suffix,body,method})=>{const site=new URL(location.href).searchParams.get('sede');const csrf=await fetch('/api/v1/sesion/csrf').then(r=>r.json());const r=await fetch('/api/v1/sedes/'+site+suffix,{method,headers:{'Content-Type':'application/json',[csrf.headerName]:csrf.token,'Idempotency-Key':crypto.randomUUID()},...(body===undefined?{}:{body:JSON.stringify(body)})});const data=await r.json();if(!r.ok)throw new Error(JSON.stringify(data));return data;},{suffix,body,method});}

class Recording{
    t0=0;tPage=0;cues:{start:number;end?:number;text:string}[]=[];page!:Page;
    constructor(readonly id:string,readonly title:string,readonly subtitle:string){}
    async open(hash:string){
        this.page=await shared.context!.newPage();this.tPage=Date.now();await this.page.addInitScript(CURSOR);
        await this.page.goto('/'+shared.search+'#'+hash);await this.page.locator('#main-title').waitFor();await expect(this.page.locator('.loading')).toHaveCount(0);await this.page.waitForTimeout(400);
        this.t0=Date.now();
        await this.page.evaluate(([t,s])=>{const o=document.createElement('div');o.setAttribute('aria-hidden','true');const add=(tag:string,text:string,css:string)=>{const e=document.createElement(tag);e.textContent=text;e.style.cssText=css;o.appendChild(e);};add('p','BoviCierre · Video de uso','margin:0 0 6px;font:600 13px/1 Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#E6C877');add('h2',t,'margin:0;font:700 34px/1.15 Inter,sans-serif;letter-spacing:-.03em;color:#fff');add('p',s,'margin:10px 0 0;font:400 17px/1.5 Inter,sans-serif;color:#DCE8E0');Object.assign(o.style,{position:'fixed',inset:'0',display:'grid',placeContent:'center',textAlign:'center',padding:'40px',background:'radial-gradient(60% 60% at 50% 40%,rgba(14,34,25,.93),rgba(5,15,10,.97))',zIndex:'2147483646',transition:'opacity .6s'});document.body.appendChild(o);setTimeout(()=>{o.style.opacity='0';},2600);setTimeout(()=>o.remove(),3300);},[this.title,this.subtitle]);
        this.say(this.title);await this.page.waitForTimeout(3300);
    }
    say(text:string){const now=(Date.now()-this.t0)/1000;const last=this.cues.at(-1);if(last&&last.end===undefined)last.end=Math.max(last.start+1.2,now);this.cues.push({start:now,text});}
    async point(l:Locator){await l.scrollIntoViewIfNeeded();const b=await l.boundingBox();if(b){await this.page.mouse.move(b.x+b.width/2,b.y+b.height/2,{steps:22});await this.page.waitForTimeout(260);}}
    async click(l:Locator){await this.point(l);await l.click();await this.page.waitForTimeout(700);}
    async type(l:Locator,value:string){await this.point(l);await l.click();await l.pressSequentially(value,{delay:55});await this.page.waitForTimeout(350);}
    async choose(l:Locator,option:{label?:string;index?:number}|string){await this.point(l);await l.selectOption(option as never);await this.page.waitForTimeout(500);}
    async pause(ms=1200){await this.page.waitForTimeout(ms);}
    async submit(l:Locator,path:RegExp,method='POST'){const res=this.page.waitForResponse(x=>path.test(new URL(x.url()).pathname)&&x.request().method()===method);await this.click(l);const r=await res;expect(r.status(),await r.text()).toBeLessThan(300);await this.pause(900);return r.json().catch(()=>({}));}
    async finish(){
        await this.pause(1500);const end=(Date.now()-this.t0)/1000;const last=this.cues.at(-1);if(last&&last.end===undefined)last.end=end;
        const video=this.page.video()!;await this.page.close();const raw=resolve(OUT,this.id+'.webm');await video.saveAs(raw);
        const offset=((this.t0-this.tPage)/1000).toFixed(2);const mp4=resolve(OUT,this.id+'.mp4');
        execFileSync('ffmpeg',['-y','-loglevel','error','-ss',offset,'-i',raw,'-vf','scale=1280:720:flags=lanczos,format=yuv420p','-c:v','libx264','-preset','slow','-crf','27','-movflags','+faststart','-an',mp4]);
        execFileSync('ffmpeg',['-y','-loglevel','error','-ss','4.2','-i',mp4,'-frames:v','1','-q:v','4',resolve(OUT,this.id+'-poster.jpg')]);
        await unlink(raw);
        const ts=(s:number)=>{const ms=Math.round(s*1000);const h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,sec=Math.floor(ms/1000)%60;return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}.${String(ms%1000).padStart(3,'0')}`;};
        await writeFile(resolve(OUT,this.id+'.vtt'),'WEBVTT\n\n'+this.cues.map((c,i)=>`${i+1}\n${ts(c.start)} --> ${ts(c.end!)}\n${c.text}\n`).join('\n'));
    }
}

test.beforeAll(async({browser})=>{
    await mkdir(OUT,{recursive:true});shared.context=await browser.newContext({recordVideo:{dir:'/tmp/bovicierre-tutorials',size:{width:1280,height:720}},viewport:{width:1280,height:720}});
    const page=await shared.context.newPage();await page.goto('/');await page.getByLabel('Usuario *',{exact:true}).fill('demo.admin');await page.getByLabel('Contraseña *',{exact:true}).fill(await password());await page.getByRole('button',{name:'Ingresar',exact:true}).click();
    await page.getByRole('button',{name:/DEMO Sede A/}).click();await page.locator('#main-title').waitFor();shared.search=new URL(page.url()).search;
    await api(page,'/contrapartes',{nombre:party,tipo_persona:'MORAL'});
    for(const n of [1,2])shared.animals.push((await api(page,'/animales',{sexo:'M',identificaciones:[{sistema:'INTERNO',codigo:`DEMO-VID-${run}-${n}`}]})).id);
    await page.close();
});
test.afterAll(async()=>{await shared.context?.close();});

async function pickParty(r:Recording){const form=r.page.locator('form').filter({has:r.page.locator('[name="parte_id"]')}).first();await r.type(form.locator('[name="buscar_parte_id"]'),party);await r.click(form.getByRole('button',{name:'Buscar contraparte',exact:true}));await expect(form.locator('[name="parte_id"] option').filter({hasText:party})).toHaveCount(1);await r.choose(form.locator('[name="parte_id"]'),{label:party});}
async function lot(r:Recording,price:string){
    r.say('Busca el ganado por su arete y márcalo en la lista.');await r.type(r.page.locator('[name="busqueda_ganado"]'),'DEMO-VID-'+run);await r.click(r.page.getByRole('button',{name:'Buscar ganado',exact:true}));
    for(const id of shared.animals)await r.click(r.page.locator(`label.check-row[data-animal="${id}"]`).getByRole('checkbox'));
    r.say('Indica el precio: por cabeza o por kilo. El importe final lo calcula el servidor.');await r.choose(r.page.locator('[name="unidad_precio"]'),'CABEZA');await r.type(r.page.locator('[name="precio_unitario"]'),price);
    await r.submit(r.page.getByRole('button',{name:'Guardar condiciones del lote',exact:true}),/\/operaciones\/[^/]+$/,'PATCH');
    r.say('Acepta las condiciones pactadas con la contraparte.');await r.submit(r.page.getByRole('button',{name:'Aceptar condiciones',exact:true}),/\/acordar$/);
}
async function confirm(r:Recording,kind:'compra'|'venta'){
    r.say('Revisa el cálculo del servidor y confirma: sólo aquí nace la deuda.');await r.click(r.page.getByRole('button',{name:'3 · Revisar y confirmar'}));
    const form=r.page.locator('form').filter({has:r.page.getByRole('button',{name:'Confirmar '+kind,exact:true})});await expect.poll(()=>form.locator('[name="periodo_id"] option').count()).toBeGreaterThan(1);await r.choose(form.locator('[name="periodo_id"]'),{index:1});
    const done=r.page.waitForResponse(x=>x.url().includes('/confirmar')&&x.request().method()==='POST');await r.click(form.getByRole('button',{name:'Confirmar '+kind,exact:true}));const res=await done;expect(res.status()).toBeLessThan(300);await r.pause(1600);return await res.json() as {id:string};
}

test('compra',async()=>{
    const r=new Recording('compra','Comprar ganado y confirmar el trato','Del borrador a la liquidación en cuatro pasos');await r.open('operaciones');
    r.say('Desde la Bandeja, empieza una nueva operación.');await r.click(r.page.getByRole('button',{name:'+ Nueva operación'}));
    r.say('Elige el tipo de trato y al proveedor.');await r.choose(r.page.locator('[name="tipo"]'),'COMPRA');await pickParty(r);await r.click(r.page.locator('[name="requiere_recepcion"]'));
    const created=r.page.waitForResponse(x=>x.url().endsWith('/operaciones')&&x.request().method()==='POST');await r.click(r.page.getByRole('button',{name:'Crear borrador',exact:true}));shared.purchase=(await (await created).json()).id;
    r.say('El borrador todavía no genera inventario ni saldo.');await r.pause(900);
    await lot(r,'10000');await confirm(r,'compra');
    r.say('Listo: la compra quedó confirmada y su liquidación muestra el total exacto.');await r.finish();
});
test('recepcion',async()=>{
    const r=new Recording('recepcion','Recibir el ganado comprado','La recepción física no cambia el importe');await r.open('captura/'+shared.purchase);
    const panel=r.page.locator('.panel').filter({has:r.page.getByRole('heading',{name:'Recibir ganado'})});
    r.say('Abre la compra confirmada: el panel Recibir ganado muestra los animales pendientes.');await r.point(panel.getByRole('heading',{name:'Recibir ganado'}));await r.pause(900);
    r.say('Marca los animales que llegaron. Puedes seleccionar toda la página.');await r.click(panel.getByRole('checkbox',{name:/Seleccionar los/}));
    r.say('Indica la fecha y hora de llegada y confirma la recepción.');await r.point(panel.locator('[name="ocurrido_en"]'));await panel.locator('[name="ocurrido_en"]').fill('2026-10-14T09:30');await r.pause(500);
    await r.submit(panel.getByRole('button',{name:'Confirmar recepción'}),/\/inventario\/movimientos$/);
    r.say('El ganado queda disponible para venta, con su costo intacto.');await r.finish();
});
test('venta-cobro',async()=>{
    const r=new Recording('venta-cobro','Vender, entregar y cobrar','Reserva, confirmación, entrega y cobro aplicado');await r.open('captura');
    r.say('Crea el borrador de venta con el comprador.');await r.choose(r.page.locator('[name="tipo"]'),'VENTA');await pickParty(r);
    const created=r.page.waitForResponse(x=>x.url().endsWith('/operaciones')&&x.request().method()==='POST');await r.click(r.page.getByRole('button',{name:'Crear borrador',exact:true}));shared.sale=(await (await created).json()).id;
    await lot(r,'16000');
    r.say('Reserva el ganado: nadie más podrá venderlo mientras la reserva esté activa.');const due=await r.page.evaluate(()=>{const d=new Date(Date.now()+3600000);const p=(v:number)=>String(v).padStart(2,'0');return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;});await r.point(r.page.locator('[name="vence_en"]'));await r.page.locator('[name="vence_en"]').fill(due);await r.submit(r.page.getByRole('button',{name:'Reservar posiciones',exact:true}),/\/reservas$/);
    const settlement=await confirm(r,'venta');
    r.say('La entrega es un paso físico aparte: marca los animales entregados.');const deliver=r.page.locator('.panel').filter({has:r.page.getByRole('heading',{name:'Registrar entrega'})});
    if(!await deliver.count()){await r.page.goto('/'+shared.search+'#captura/'+shared.sale);await r.page.locator('#main-title').waitFor();}
    await r.click(deliver.getByRole('checkbox',{name:/Seleccionar los/}));await deliver.locator('[name="ocurrido_en"]').fill('2026-10-14T12:00');await r.submit(deliver.getByRole('button',{name:'Confirmar entrega'}),/\/inventario\/movimientos$/);
    r.say('Para cobrar, abre la liquidación y registra el dinero recibido.');
    await r.page.goto('/'+shared.search+'#liquidaciones/'+settlement.id);await r.page.locator('#main-title').waitFor();await expect(r.page.locator('.loading')).toHaveCount(0);await r.pause(1400);
    await r.click(r.page.getByRole('button',{name:'Registrar cobro',exact:true}));await pickParty(r);await r.type(r.page.locator('[name="importe"]').first(),'32000');await r.choose(r.page.locator('[name="metodo"]').first(),'TRANSFERENCIA');
    const paid=r.page.waitForResponse(x=>x.url().endsWith('/pagos')&&x.request().method()==='POST');await r.click(r.page.getByRole('button',{name:'Registrar dinero',exact:true}));const payment=await (await paid).json();
    r.say('Valida el pago y aplícalo a la liquidación: el saldo se actualiza al momento.');const validate=r.page.locator('form').filter({has:r.page.getByRole('button',{name:'Validar pago revisado'})});await expect.poll(()=>validate.locator('[name="periodo_id"] option').count()).toBeGreaterThan(1);await r.choose(validate.locator('[name="periodo_id"]'),{index:1});await r.click(validate.getByRole('button',{name:'Validar pago revisado'}));
    const compatible=r.page.locator('.panel').filter({has:r.page.getByRole('heading',{name:/Disponible de/})});await r.click(compatible.locator('tbody tr').filter({hasText:settlement.id}).getByRole('button',{name:/Abrir/}));
    const apply=r.page.locator('form').filter({has:r.page.getByRole('button',{name:'Aplicar pago a liquidación'})});await r.type(apply.locator('[name="importe"]'),'32000');await expect.poll(()=>apply.locator('[name="periodo_id"] option').count()).toBeGreaterThan(1);await r.choose(apply.locator('[name="periodo_id"]'),{index:1});
    const applied=r.page.waitForResponse(x=>x.url().endsWith('/pagos/'+payment.id+'/aplicaciones'));await r.click(apply.getByRole('button',{name:'Aplicar pago a liquidación'}));expect((await applied).status()).toBeLessThan(300);
    r.say('Cobro aplicado: la cuenta del comprador queda en cero.');await r.finish();
});
test('tablero',async()=>{
    const r=new Recording('tablero','Tablero, cartera y margen','Lo pendiente de la sede y el resultado del servidor');await r.open('operaciones');
    r.say('La Bandeja resume lo pendiente con conteos del servidor.');const board=r.page.getByRole('region',{name:'Pendientes de la sede'});await r.point(board);await r.pause(1800);
    r.say('Cada tarjeta lleva a su pantalla. Por ejemplo, lo que hay por cobrar.');await r.click(board.locator('[data-task="Por cobrar"]'));await expect(r.page.locator('.loading')).toHaveCount(0);await r.pause(1600);
    r.say('El margen muestra el resultado calculado por el servidor y su fecha de corte.');await r.page.goto('/'+shared.search+'#margen');await r.page.locator('#main-title').waitFor();await expect(r.page.locator('.loading')).toHaveCount(0);await r.point(r.page.locator('.margin-bars'));await r.pause(2400);
    r.say('En Ayuda y tutoriales encuentras este y otros videos, y un recorrido guiado.');await r.click(r.page.locator('.sidebar a[href="#ayuda"]'));await r.pause(1200);
    await r.click(r.page.getByRole('button',{name:'Iniciar recorrido guiado'}));await r.pause(2600);const tour=r.page.getByRole('dialog');await r.click(tour.getByRole('button',{name:'Siguiente'}));await r.pause(2600);await r.click(tour.getByRole('button',{name:'Saltar'}));
    r.say('Así de simple: del trato al cierre, con cada saldo explicado.');await r.finish();
});
