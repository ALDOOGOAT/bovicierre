import {expect,type Page} from '@playwright/test';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {homedir} from 'node:os';
import {test} from './runtime';
// Capturas de sólo lectura (sin mutaciones) para comparar antes/después del rediseño.
// BOVI_SHOT_DIR=<dir> npm run test:e2e -- visual.spec.ts
const out=process.env.BOVI_SHOT_DIR||'/tmp/bovicierre-shots';
const widths=[390,768,1440];
const screens=['operaciones','captura','inventario','animales','pesajes','liquidaciones','pagos','expediente','cartera','margen','periodos'];
async function login(page:Page){
    const secret=(await readFile(homedir()+'/.local/share/bovicierre-academic/secrets/demo_password','utf8')).trim();
    await page.goto('/');await page.getByLabel('Usuario *',{exact:true}).fill('demo.admin');await page.getByLabel('Contraseña *',{exact:true}).fill(secret);
    await page.getByRole('button',{name:'Ingresar',exact:true}).click();await expect(page.getByRole('heading',{name:'Selecciona una sede'})).toBeVisible();
}
async function settle(page:Page){await page.waitForLoadState('networkidle');await expect(page.locator('.loading')).toHaveCount(0,{timeout:20000});
    // Captura sólo cuando terminaron las entradas animadas (las infinitas, como la deriva de la foto, se ignoran).
    await page.evaluate(()=>Promise.all(document.getAnimations().filter(a=>a.effect?.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>undefined))));}
async function overflow(page:Page){return page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);}
test('capturas del recorrido principal',async({page})=>{
    await mkdir(out,{recursive:true});const report:Record<string,unknown>[]=[];
    for(const width of widths){
        await page.setViewportSize({width,height:width<768?844:1000});await page.context().clearCookies();
        await page.goto('/');await settle(page);await page.screenshot({path:`${out}/${width}-login.png`,fullPage:true});report.push({width,screen:'login',overflow:await overflow(page)});
        await login(page);await settle(page);await page.screenshot({path:`${out}/${width}-sede.png`,fullPage:true});report.push({width,screen:'sede',overflow:await overflow(page)});
        await page.getByRole('button',{name:/DEMO Sede A/}).click();await settle(page);
        const site=new URL(page.url()).searchParams.get('sede');
        for(const screen of screens){
            await page.goto(`/?sede=${site}#${screen}`);await settle(page);
            await page.screenshot({path:`${out}/${width}-${screen}.png`,fullPage:true});report.push({width,screen,overflow:await overflow(page)});
        }
        // Detalles de solo lectura: primera liquidación y primer expediente con datos.
        for(const [screen,label] of [['liquidaciones','liquidacion-detalle'],['expediente','expediente-detalle']]){
            await page.goto(`/?sede=${site}#${screen}`);await settle(page);const open=page.getByRole('button',{name:/Abrir/}).first();
            if(await open.count()){await open.waitFor({state:'visible',timeout:45000});await open.click({timeout:45000});await settle(page);await page.screenshot({path:`${out}/${width}-${label}.png`,fullPage:true});report.push({width,screen:label,overflow:await overflow(page)});}
        }
    }
    await writeFile(`${out}/report.json`,JSON.stringify(report,null,2));
    expect(report.filter(r=>r.overflow)).toEqual([]);
});
