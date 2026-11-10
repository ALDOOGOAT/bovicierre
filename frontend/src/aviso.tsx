// Avisos de «ya quedó apuntado» (2026-11-10). Sonner pone la fila, el apilado y el cierre automático;
// el papelito es nuestro (toast.custom): una tira de la libreta con su renglón y un sello «APUNTADO».
// Solo confirma lo que el servidor ya guardó: no lleva botones, no reintenta nada y no tapa clics
// (pointer-events: none en usabilidad.css). Los errores nunca van aquí: se quedan junto al formulario.
// Su hoja de estilos viaja en el CSS empaquetado (main.tsx); vite.config.ts quita el <style> en línea de Sonner.
import {Toaster, toast} from 'sonner';

export function Avisos() {
  return (
    <Toaster
      position="bottom-right"
      offset={{bottom: '24px', right: '24px'}}
      mobileOffset={{bottom: '12px', left: '12px', right: '12px'}}
      visibleToasts={3}
      gap={10}
      containerAriaLabel="Avisos de la libreta"
      toastOptions={{duration: 4200}}
    />
  );
}

function Papelito({titulo, detalle}: {titulo: string; detalle?: string}) {
  return (
    <div className="papelito">
      <span className="papelito-sello" aria-hidden="true">
        <svg viewBox="0 0 20 20" width="16" height="16" focusable="false">
          <path d="M4.5 10.5l3.6 3.4 7.4-8" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Apuntado
      </span>
      <p className="papelito-texto">
        <strong>{titulo}</strong>
        {detalle && <small>{detalle}</small>}
      </p>
    </div>
  );
}

/** Confirma una acción guardada. El id estable evita avisos duplicados si el mismo resultado llega dos veces. */
export function avisarGuardado(titulo: string, detalle?: string, id?: string) {
  if (typeof document === 'undefined') return;
  toast.custom(() => <Papelito titulo={titulo} detalle={detalle} />, id ? {id} : undefined);
}
