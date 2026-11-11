import {test} from './runtime';
import {expect,type Page} from '@playwright/test';
import {readFile} from 'node:fs/promises';
import {homedir} from 'node:os';

// Registro detallado seguro (2026-11-11): cambiar de paso con cambios sin guardar pregunta antes,
// y «Confirmar» sólo se habilita con las condiciones aceptadas (no se confirma una versión anterior por error).
const base='/api/v1';
const PARTE='DEMO ACUERDO mwadx36t';
const password=()=>readFile(homedir()+'/.local/share/bovicierre-academic/secrets/demo_password','utf8').then(v=>v.trim());
async function login(page:Page){
    await page.goto('/');await page.getByLabel('Usuario *',{exact:true}).fill('demo.admin');await page.getByLabel('Contraseña *',{exact:true}).fill(await password());await page.getByRole('button',{name:'Ingresar',exact:true}).click();
    await page.getByRole('heading',{name:'Selecciona una sede'}).waitFor();await page.getByRole('button',{name:/DEMO Sede A/}).click();await page.getByRole('heading',{name:'Bandeja',exact:true}).waitFor();
}
async function navigate(page:Page,hash:string){await page.goto('/'+(new URL(page.url()).search)+'#'+hash);await page.locator('#main-title').waitFor();await expect(page.locator('.loading')).toHaveCount(0);}
async function borrador(page:Page){
    await navigate(page,'captura');await page.locator('[name="tipo"]').selectOption('COMPRA');
    if(!await page.locator('[name="parte_id"] option').filter({hasText:PARTE}).count()){await page.locator('[name="buscar_parte_id"]').fill(PARTE);await page.getByRole('button',{name:'Buscar contraparte',exact:true}).click();}
    await page.locator('[name="parte_id"]').selectOption({label:PARTE});
    const creada=page.waitForResponse(r=>r.url().includes(base)&&r.url().split('?')[0].endsWith('/operaciones')&&r.request().method()==='POST');
    await page.getByRole('button',{name:'Crear borrador',exact:true}).click();expect((await creada).status()).toBeLessThan(300);
    await page.getByRole('button',{name:'1 · Ganado y precio',exact:true}).waitFor();
}

test('registro detallado: avisa al cambiar de paso con cambios y no confirma sin aceptar',async({page})=>{
    await login(page);await borrador(page);
    // Un precio escrito y no guardado cuenta como cambio pendiente.
    await page.locator('[name="precio_unitario"]').fill('52.50');
    await page.getByRole('button',{name:'3 · Revisar y confirmar',exact:true}).click();
    const aviso=page.getByRole('alert').filter({hasText:'Tienes cambios sin guardar en «1 · Ganado y precio».'});
    await expect(aviso).toBeVisible();
    await aviso.getByRole('button',{name:'Seguir en Ganado y precio',exact:true}).click();
    await expect(aviso).toHaveCount(0);
    await expect(page.locator('[name="precio_unitario"]')).toHaveValue('52.50');
    // Elegir irse sin guardar sí cambia de paso.
    await page.getByRole('button',{name:'3 · Revisar y confirmar',exact:true}).click();
    await aviso.getByRole('button',{name:'Ir a «Revisar y confirmar» sin guardar',exact:true}).click();
    await expect(page.getByRole('heading',{name:'Revisión del cierre económico'})).toBeVisible();
    // En BORRADOR «Confirmar» se bloquea y se dice por qué, con salida a aceptar.
    await expect(page.getByText('Las condiciones todavía no están aceptadas.')).toBeVisible();
    await expect(page.getByRole('button',{name:'Confirmar compra',exact:true})).toBeDisabled();
    await expect(page.getByText('Primero acepta las condiciones en «1 · Ganado y precio».')).toBeVisible();
    await page.getByRole('button',{name:'Ir a aceptar condiciones',exact:true}).click();
    await expect(page.getByRole('button',{name:'Guardar condiciones del lote',exact:true})).toBeVisible();
    // Sin cambios pendientes, cambiar de paso no pregunta.
    await page.getByRole('button',{name:'2 · Pesaje',exact:true}).click();
    await expect(page.getByRole('heading',{name:'Proponer ticket de báscula'})).toBeVisible();
    await expect(page.getByRole('alert').filter({hasText:'cambios sin guardar'})).toHaveCount(0);
});
