import {test as base} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
export const test=base.extend<{runtimeLog:void}>({runtimeLog:[async({page},use,info)=>{
 const record={console_errors:[] as string[],page_errors:[] as string[],http_errors:[] as {status:number;path:string}[]};page.on('console',m=>{if(m.type()==='error')record.console_errors.push(m.text());});page.on('pageerror',e=>record.page_errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/v1/')&&r.status()>=400)record.http_errors.push({status:r.status(),path:new URL(r.url()).pathname});});await use();await writeFile('/tmp/bovicierre-ui-runtime-'+info.testId.replace(/[^A-Za-z0-9_-]/g,'_')+'.json',JSON.stringify({title:info.title,status:info.status,duration_ms:info.duration,base_url:info.project.use.baseURL,...record},null,2));
 },{auto:true}]});
