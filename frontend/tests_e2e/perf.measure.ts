import {test,expect,type Page} from '@playwright/test';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {homedir} from 'node:os';
import {resolve} from 'node:path';
// Medición de fluidez del rediseño v4 en el Chrome real del equipo (GPU que Chrome elija; se registra cuál).
// Cada escenario cuenta cuadros con requestAnimationFrame con movimiento normal y con prefers-reduced-motion,
// para aislar el costo de las animaciones. Salida: docs/testing/evidence/performance/ui-v4-intel.json.
type Stats={frames:number;fps:number;p95_ms:number;max_ms:number;sobre_33ms:number};
async function frames(page:Page,ms:number,during?:()=>Promise<void>):Promise<Stats>{
    await page.evaluate(()=>{const w=window as unknown as {__d:number[];__run:boolean};w.__d=[];w.__run=true;let last=performance.now();const tick=(t:number)=>{w.__d.push(t-last);last=t;if(w.__run)requestAnimationFrame(tick);};requestAnimationFrame(tick);});
    const start=Date.now();if(during)await during();const rest=ms-(Date.now()-start);if(rest>0)await page.waitForTimeout(rest);
    return page.evaluate(()=>{const w=window as unknown as {__d:number[];__run:boolean};w.__run=false;const d=w.__d.slice(1).sort((a,b)=>a-b);const total=d.reduce((a,b)=>a+b,0);
        return {frames:d.length,fps:Math.round(d.length/(total/1000)*10)/10,p95_ms:Math.round(d[Math.floor(d.length*.95)]*10)/10,max_ms:Math.round(d[d.length-1]*10)/10,sobre_33ms:d.filter(x=>x>33.4).length};});
}
test('fluidez v4 en GPU real',async({page,browser})=>{
    const cdp=await browser.newBrowserCDPSession();const info=await cdp.send('SystemInfo.getInfo');await cdp.detach();
    const secret=(await readFile(homedir()+'/.local/share/bovicierre-academic/secrets/demo_password','utf8')).trim();
    await page.goto('/');await page.getByLabel('Usuario *',{exact:true}).fill('demo.admin');await page.getByLabel('Contraseña *',{exact:true}).fill(secret);await page.getByRole('button',{name:'Ingresar',exact:true}).click();
    await page.getByRole('button',{name:/DEMO Sede A/}).click();await expect(page.locator('#main-title')).toHaveText('Bandeja');await page.evaluate(()=>localStorage.setItem('bovi.tour.voz','off'));
    const results:Record<string,unknown>[]=[];
    for(const motion of ['no-preference','reduce'] as const){
        await page.emulateMedia({reducedMotion:motion});const tag=motion==='reduce'?'reducido':'normal';
        await page.reload();await expect(page.locator('.loading')).toHaveCount(0);
        results.push({nombre:'bandeja-reposo (aurora + conteo animado)',movimiento:tag,...await frames(page,4000)});
        results.push({nombre:'navegacion entre 6 secciones (bandas + entrada)',movimiento:tag,...await frames(page,6000,async()=>{for(const id of ['inventario','liquidaciones','margen','periodos','ayuda','operaciones']){await page.locator(`.sidebar a[href="#${id}"]`).click();await page.waitForTimeout(800);}})});
        results.push({nombre:'recorrido guiado (realce y tarjeta)',movimiento:tag,...await frames(page,4500,async()=>{await page.getByRole('button',{name:'Recorrido guiado',exact:true}).click();const tour=page.getByRole('dialog');for(let i=0;i<3;i++){await page.waitForTimeout(700);await tour.getByRole('button',{name:'Siguiente'}).click();}await page.keyboard.press('Escape');})});
        await page.locator('.sidebar a[href="#inventario"]').click();await expect(page.locator('.loading')).toHaveCount(0);
        results.push({nombre:'desplazamiento de tabla bajo barra translúcida',movimiento:tag,...await frames(page,3000,async()=>{await page.evaluate(()=>new Promise<void>(done=>{let y=0;const step=()=>{y+=24;window.scrollTo(0,y);if(y<2400)requestAnimationFrame(step);else done();};requestAnimationFrame(step);}));})});
    }
    const out=resolve('../docs/testing/evidence/performance');await mkdir(out,{recursive:true});
    const report={medido_en:new Date().toISOString(),gpu:info.gpu.auxAttributes?.glRenderer,ventana:page.viewportSize(),escenarios:results};
    await writeFile(resolve(out,'ui-v4-intel.json'),JSON.stringify(report,null,1)+'\n');console.log(JSON.stringify(report,null,1));
    for(const r of results)expect(r.fps as number,String(r.nombre)).toBeGreaterThan(30);
});
