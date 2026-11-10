import {defineConfig,type Plugin} from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Sonner sin <style> en línea (2026-11-10). Su dist llama `__insertCSS("…")` al evaluarse y mete un <style> que la CSP
 * del despliegue (infra/caddy: style-src 'self') bloquea. La misma hoja ya viaja en el CSS empaquetado
 * (main.tsx importa 'sonner/dist/styles.css'), así que aquí se quita esa llamada del módulo de Sonner.
 * Si Sonner cambia su dist y la llamada no aparece, el build falla a propósito: mejor eso que un error de CSP callado.
 * En `vite dev` (sin Caddy ni CSP) la dependencia va preempaquetada y conserva su <style>; no hace daño.
 */
function sonnerSinEstiloEnLinea():Plugin{
    return {
        name:'bovi:sonner-sin-estilo-en-linea',
        enforce:'pre',
        transform(code,id){
            if(!/[\\/]node_modules[\\/]sonner[\\/]dist[\\/]index\.m?js$/.test(id.split('?')[0]))return null;
            const sin=code.replace(/^__insertCSS\(".*"\);?$/m,'');
            if(sin===code)this.error('Sonner ya no trae la llamada __insertCSS esperada: revisa el plugin sonnerSinEstiloEnLinea (CSP style-src).');
            return {code:sin,map:null};
        },
    };
}

export default defineConfig({plugins:[sonnerSinEstiloEnLinea(),react()],server:{host:'127.0.0.1',port:15173,strictPort:true,proxy:{'/api':{target:'http://127.0.0.1:18080',changeOrigin:false}}}});
