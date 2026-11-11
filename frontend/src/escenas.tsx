// Ilustraciones propias de BoviCierre (brief de identidad, 2026-11-09): objetos reales del trato ganadero dibujados en SVG.
// Línea de tinta + relleno plano. Decorativas (aria-hidden): el texto equivalente siempre está en la interfaz.
// Los momentos firma se activan con la clase `is-playing` y se animan en identidad.css; con movimiento reducido quedan estáticos.
import type { ReactNode } from "react";
import { letraBascula } from "./caminos-util";

const INK = "var(--tinta)";

function Svg({ viewBox, className, children }: { viewBox: string; className?: string; children: ReactNode }) {
  return (
    <svg className={"escena " + (className || "")} viewBox={viewBox} aria-hidden="true" focusable="false">
      {children}
    </svg>
  );
}

/** Silueta de cebú de perfil (joroba alta, orejas caídas, papada): el ganado del trópico mexicano. Caja ≈ 106×68. */
export function Cebu({ className, x = 0, y = 0, s = 1 }: { className?: string; x?: number; y?: number; s?: number }) {
  return (
    <g className={"cebu " + (className || "")} transform={`translate(${x} ${y}) scale(${s})`}>
      {/* patas (detrás del cuerpo) con pezuña oscura */}
      <path d="M15 38l1 28h5l1-26zM26 42v24h5l1-24zM64 44l-1 22h5l1-22zM73 44l1 22h5l-1-22z" fill="var(--hueso-sombra)" stroke={INK} strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M15.5 63h6M26 63h5.5M62.6 63h5.6M74 63h5.6" stroke={INK} strokeWidth="3" />
      {/* cuerpo, joroba, cuello, cabeza y papada */}
      <path
        d="M10 24C10 18 16 15 24 15H56C58 9 64 5 70 6C75 7 77 11 78 15C82 15 86 13 89 14C93 15 97 20 100 26L104 33C105 36 102 38 99 37C97 37 96 38 95 40C92 46 86 52 79 53C77 53 75 51 74 49L73 47C62 49 40 49 26 47C18 46 12 42 10 36Z"
        fill="var(--hueso)"
        stroke={INK}
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      {/* sombra de la joroba */}
      <path d="M59 15c2-5 6-8 11-8 4 1 6 4 7 8z" fill="var(--hueso-sombra)" />
      {/* oreja larga caída con arete amarillo */}
      <path d="M88 17c-4 1-7 6-7 14 3-1 6-5 7-10" fill="var(--hueso-sombra)" stroke={INK} strokeWidth="1.4" strokeLinejoin="round" />
      <rect x="81" y="25" width="4" height="5" rx="1" fill="var(--arete)" stroke={INK} strokeWidth="1" />
      {/* cuerno corto */}
      <path d="M90 14c0-3 1-5 3-6" fill="none" stroke={INK} strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="94" cy="21" r="1.3" fill={INK} />
      <path d="M100 33.5c1.2.2 2 .8 2.3 1.6" fill="none" stroke={INK} strokeWidth="1.2" strokeLinecap="round" />
      {/* cola con borla */}
      <path d="M11 24c-4 4-5 12-4 20" fill="none" stroke={INK} strokeWidth="1.6" strokeLinecap="round" />
      <path d="M7 43c-2 2-2 5 0 7 2-2 3-5 0-7z" fill={INK} />
    </g>
  );
}

/** Arete SINIIGA: el número del animal sobre plástico amarillo. Componente HTML (no SVG) para que el código sea texto real. */
export function Arete({ code, selected, muted }: { code: string; selected?: boolean; muted?: boolean }) {
  return (
    <span className={"arete" + (selected ? " is-selected" : "") + (muted ? " is-muted" : "")}>
      <span className="arete-code">{code}</span>
    </span>
  );
}

/** Báscula ganadera de plataforma con barandal y pantalla. `kg` es el peso que muestra la pantalla (texto, no animado). */
export function Bascula({ kg, play, className }: { kg?: string; play?: boolean; className?: string }) {
  // «910.500» o «4,520.500» no caben a 15: la letra se achica para quedarse dentro de la pantalla (y centrada en alto).
  const lectura = kg || "0";
  const letra = letraBascula(lectura);
  return (
    <Svg viewBox="0 0 240 130" className={"bascula " + (play ? "is-playing " : "") + (className || "")}>
      <rect x="0" y="118" width="240" height="12" fill="var(--tierra)" />
      {/* poste y pantalla */}
      <rect x="196" y="40" width="8" height="80" fill="var(--madera-oscura)" stroke={INK} strokeWidth="1.6" />
      <rect x="172" y="14" width="58" height="34" rx="4" fill="var(--potrero)" stroke={INK} strokeWidth="1.8" />
      <rect x="178" y="20" width="46" height="20" rx="2" fill="var(--pantalla)" />
      <text className="bascula-lectura" x="221" y={30 + letra * 0.36} textAnchor="end" style={{ fontSize: letra }}>
        {lectura}
      </text>
      <text className="bascula-unidad" x="201" y="45" textAnchor="middle">
        KG
      </text>
      <g className="plataforma">
        {/* barandal */}
        <path d="M18 72V104M60 72V104M102 72V104M144 72V104M14 74H150M14 88H150" fill="none" stroke="var(--madera-oscura)" strokeWidth="4" strokeLinecap="round" />
        <path d="M18 72V104M60 72V104M102 72V104M144 72V104M14 74H150M14 88H150" fill="none" stroke={INK} strokeWidth="1" opacity=".35" />
        <Cebu x={34} y={48} s={0.82} />
        {/* plataforma de tablones */}
        <rect x="8" y="104" width="150" height="12" rx="2" fill="var(--madera)" stroke={INK} strokeWidth="1.8" />
        <path d="M38 104v12M68 104v12M98 104v12M128 104v12" stroke={INK} strokeWidth="1" opacity=".4" />
      </g>
      <path className="cable" d="M158 112c14 0 20-4 38-6" fill="none" stroke={INK} strokeWidth="1.4" strokeDasharray="3 3" />
    </Svg>
  );
}

/** Fierro de herrar y la marca del trato (una B y una C unidas sobre media luna, al estilo de los fierros de herradero).
 * Al reproducirse, el fierro baja, marca y la brasa se apaga. */
const MARCA = "M84 66v44M84 66h12c8 0 12 4 12 10s-4 10-12 10H84M84 86h14c8 0 12 4 12 12s-4 12-12 12H84M150 72c-4-5-9-7-15-7-12 0-18 9-18 23s6 23 18 23c6 0 11-2 15-7M80 126c18 10 52 10 72 0";
export function Fierro({ play, className, label = "TRATO CERRADO" }: { play?: boolean; className?: string; label?: string }) {
  return (
    <Svg viewBox="0 0 232 164" className={"fierro " + (play ? "is-playing " : "") + (className || "")}>
      <g className="marca">
        <path className="brasa-halo" d={MARCA} fill="none" stroke="var(--brasa)" strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" opacity="0" />
        <path d={MARCA} fill="none" stroke="var(--quemado)" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        <text className="fierro-texto" x="116" y="156" textAnchor="middle">
          {label}
        </text>
      </g>
      <g className="herramienta">
        <path d="M116 6v40" stroke="var(--fierro)" strokeWidth="5" strokeLinecap="round" />
        <rect x="107" y="0" width="18" height="13" rx="3" fill="var(--cuero)" stroke={INK} strokeWidth="1.4" />
        <path d="M106 48h20" stroke="var(--fierro)" strokeWidth="5" strokeLinecap="round" />
        <path className="brasa-punta" d="M108 51h16" stroke="var(--brasa)" strokeWidth="3" strokeLinecap="round" />
      </g>
      <g className="humo" fill="none" stroke="var(--madera)" strokeWidth="2" strokeLinecap="round">
        <path d="M92 58c-4-6 4-8 0-14" />
        <path d="M140 56c-4-6 4-8 0-14" />
      </g>
    </Svg>
  );
}

/** Puerta de corral de tablones; al reproducirse se abre y el cebú entra. */
export function PuertaCorral({ play, className }: { play?: boolean; className?: string }) {
  return (
    <Svg viewBox="0 0 240 130" className={"corral " + (play ? "is-playing " : "") + (className || "")}>
      <rect x="0" y="116" width="240" height="14" fill="var(--tierra)" />
      {/* cerca fija del corral */}
      <path d="M150 52h88M150 72h88M150 92h88" stroke="var(--madera)" strokeWidth="7" />
      <path d="M150 52h88M150 72h88M150 92h88" stroke={INK} strokeWidth="1" opacity=".3" />
      <rect x="226" y="40" width="9" height="78" fill="var(--madera-oscura)" stroke={INK} strokeWidth="1.4" />
      <g className="entra">
        <Cebu x={6} y={55} s={0.9} />
      </g>
      {/* postes de la puerta */}
      <rect x="140" y="34" width="11" height="84" fill="var(--madera-oscura)" stroke={INK} strokeWidth="1.6" />
      <g className="puerta">
        <path d="M151 46h70M151 66h70M151 86h70M151 104h70" stroke="var(--madera)" strokeWidth="8" />
        <path d="M151 104L221 46" stroke="var(--madera)" strokeWidth="6" />
        <path d="M151 46h70M151 66h70M151 86h70M151 104h70M151 104L221 46" stroke={INK} strokeWidth="1" opacity=".35" fill="none" />
        <rect x="216" y="42" width="7" height="68" fill="var(--madera-oscura)" stroke={INK} strokeWidth="1.2" />
      </g>
    </Svg>
  );
}

/** Camión jaula ganadero; al reproducirse arranca y sale de cuadro. */
export function CamionJaula({ play, className }: { play?: boolean; className?: string }) {
  return (
    <Svg viewBox="0 0 240 130" className={"camion " + (play ? "is-playing " : "") + (className || "")}>
      <rect x="0" y="114" width="240" height="16" fill="var(--tierra)" />
      <path className="polvo" d="M14 108c6-6 14-6 18 0M4 100c6-4 10-4 14 0" fill="none" stroke="var(--madera)" strokeWidth="2" strokeLinecap="round" />
      <g className="vehiculo">
        {/* jaula de tablas verticales */}
        <rect x="34" y="40" width="120" height="58" rx="3" fill="var(--hueso)" stroke={INK} strokeWidth="1.8" />
        <path d="M46 42v54M58 42v54M70 42v54M82 42v54M94 42v54M106 42v54M118 42v54M130 42v54M142 42v54" stroke="var(--cuero)" strokeWidth="5" />
        <path d="M34 56h120M34 82h120" stroke={INK} strokeWidth="1.4" />
        <rect x="64" y="59" width="60" height="19" rx="2" fill="var(--hueso)" stroke="var(--tinta)" strokeWidth="1.2" />
        <text className="camion-rotulo" x="94" y="73" textAnchor="middle">
          GANADO
        </text>
        {/* cabina */}
        <path d="M156 60h34l16 18v20h-50z" fill="var(--potrero)" stroke={INK} strokeWidth="1.8" strokeLinejoin="round" />
        <path d="M164 64h22l10 12h-32z" fill="var(--pantalla)" stroke={INK} strokeWidth="1.2" />
        <rect x="30" y="96" width="178" height="8" rx="2" fill="var(--fierro)" />
        <rect x="200" y="86" width="8" height="5" rx="1" fill="var(--arete)" />
        <g className="rueda">
          <circle cx="62" cy="106" r="11" fill={INK} />
          <circle cx="62" cy="106" r="4" fill="var(--madera)" />
        </g>
        <g className="rueda">
          <circle cx="184" cy="106" r="11" fill={INK} />
          <circle cx="184" cy="106" r="4" fill="var(--madera)" />
        </g>
      </g>
    </Svg>
  );
}

/** Libreta del tratante con fajo de billetes; al reproducirse cae el sello. Las cifras nunca se animan (UXD-25). */
export function Libreta({ play, sello = "ABONADO", className }: { play?: boolean; sello?: string; className?: string }) {
  return (
    <Svg viewBox="0 0 240 130" className={"libreta " + (play ? "is-playing " : "") + (className || "")}>
      <rect x="22" y="12" width="150" height="110" rx="4" fill="var(--hoja)" stroke={INK} strokeWidth="1.8" />
      <path d="M22 12h12v110H22z" fill="var(--cuero)" stroke={INK} strokeWidth="1.4" />
      <path d="M46 36h110M46 52h110M46 68h110M46 84h110M46 100h110" stroke="var(--renglon)" strokeWidth="1.2" />
      <path d="M50 46c8-4 18-4 26 0M50 62c10-3 22-3 34 0M50 78c6-3 14-3 20 0" fill="none" stroke={INK} strokeWidth="1.2" opacity=".55" />
      {/* fajo de billetes con liga */}
      <g className="fajo">
        <rect x="150" y="70" width="74" height="38" rx="3" fill="var(--billete)" stroke={INK} strokeWidth="1.6" transform="rotate(-8 187 89)" />
        <rect x="146" y="76" width="74" height="38" rx="3" fill="var(--billete)" stroke={INK} strokeWidth="1.6" transform="rotate(4 183 95)" />
        <circle cx="183" cy="95" r="8" fill="none" stroke={INK} strokeWidth="1.2" opacity=".6" />
        <path d="M168 76c-2 12-2 26 2 38" stroke="var(--brasa)" strokeWidth="3" fill="none" />
      </g>
      <g className="sello">
        <rect x="50" y="66" width="120" height="34" rx="4" fill="none" stroke="var(--sello)" strokeWidth="3" transform="rotate(-9 110 83)" />
        <text className="sello-texto" x="110" y="90" textAnchor="middle" textLength="100" lengthAdjust="spacingAndGlyphs" transform="rotate(-9 110 83)">
          {sello}
        </text>
      </g>
    </Svg>
  );
}

/** Miniaturas para elegir método de pago (mismo trazo que las escenas). */
export function MiniPago({ metodo }: { metodo: string }) {
  if (metodo === "EFECTIVO")
    return (
      <Svg viewBox="0 0 80 50" className="mini-pago">
        <rect x="6" y="10" width="62" height="30" rx="3" fill="var(--billete)" stroke={INK} strokeWidth="1.6" transform="rotate(-6 37 25)" />
        <rect x="12" y="14" width="62" height="30" rx="3" fill="var(--billete)" stroke={INK} strokeWidth="1.6" />
        <circle cx="43" cy="29" r="6" fill="none" stroke={INK} strokeWidth="1.2" opacity=".6" />
        <path d="M26 14v30" stroke="var(--brasa)" strokeWidth="3" />
      </Svg>
    );
  if (metodo === "TRANSFERENCIA")
    return (
      <Svg viewBox="0 0 80 50" className="mini-pago">
        <rect x="26" y="3" width="28" height="44" rx="5" fill="var(--potrero)" stroke={INK} strokeWidth="1.6" />
        <rect x="30" y="9" width="20" height="28" rx="2" fill="var(--pantalla)" />
        <path d="M34 23h12m-4-4 4 4-4 4" fill="none" stroke={INK} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </Svg>
    );
  if (metodo === "CHEQUE")
    return (
      <Svg viewBox="0 0 80 50" className="mini-pago">
        <rect x="6" y="10" width="68" height="32" rx="3" fill="var(--hoja)" stroke={INK} strokeWidth="1.6" />
        <path d="M12 20h28M12 28h40M50 35c4-4 8 2 12-2 2-2 4-1 6 0" fill="none" stroke={INK} strokeWidth="1.4" strokeLinecap="round" />
      </Svg>
    );
  return (
    <Svg viewBox="0 0 80 50" className="mini-pago">
      <rect x="14" y="8" width="52" height="36" rx="4" fill="var(--hoja)" stroke={INK} strokeWidth="1.6" strokeDasharray="4 3" />
      <path d="M32 21a8 8 0 1 1 9 8v4M41 38v1" fill="none" stroke={INK} strokeWidth="2" strokeLinecap="round" />
    </Svg>
  );
}

/** Nota de remisión de papel (escena estática para "revisar el trato"). */
export function Nota({ className }: { className?: string }) {
  return (
    <Svg viewBox="0 0 120 130" className={"nota " + (className || "")}>
      <path d="M14 8h92v108l-8-6-8 6-8-6-8 6-8-6-8 6-8-6-8 6-8-6-8 6-8-6z" fill="var(--hoja)" stroke={INK} strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M26 30h68M26 44h68M26 58h46M26 72h68M26 86h30" stroke="var(--renglon)" strokeWidth="2" />
      <rect x="70" y="80" width="26" height="16" rx="2" fill="var(--arete)" stroke={INK} strokeWidth="1.2" />
    </Svg>
  );
}

/** Ilustración por camino para la mesa de inicio. */
export function EscenaCamino({ id }: { id: string }) {
  if (id === "camino-compra") return <Fierro className="mini" label="COMPRA" />;
  if (id === "camino-venta") return <Bascula kg="438" className="mini" />;
  if (id === "camino-recibir") return <PuertaCorral className="mini" />;
  if (id === "camino-entregar") return <CamionJaula className="mini" />;
  return <Libreta className="mini" sello="COBRADO" />;
}
