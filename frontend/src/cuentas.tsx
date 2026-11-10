// Cuentas legibles (2026-11-10, tanda «Dinero legible»): Liquidaciones, Cartera y Cobros y pagos se leen por folio
// del trato, contraparte y quién le debe a quién; la referencia interna queda tenue al final.
// Sin cambios en la API: el folio sale del listado de operaciones, la dirección y el total del listado de
// liquidaciones y el nombre del listado de contrapartes, cruzados por id. Ningún importe se calcula aquí.
import { useEffect, useState, type ReactNode } from 'react';
import { request } from './api';
import { type Page, type Row, text, today } from './domain';
import { cantidad, dinero, fecha, precio } from './formato';
import { conImporte, estadoCuenta, mismoImporte, palabra, quienDebe, sentidoPago } from './palabras';
import { DataTable, Estado, List, type Columna } from './ui';

type Recurso = 'operaciones' | 'liquidaciones' | 'contrapartes';
/** Lo ya encontrado, por sede y recurso. Un folio, una dirección o un nombre no cambian: no se vuelven a pedir. */
const memoria = new Map<string, Map<string, Row>>();
if (typeof window !== 'undefined') window.addEventListener('session-cleared', () => memoria.clear());

/**
 * Filas de otro listado ya existente, buscadas por id. Recorre páginas de 100 hasta encontrarlas todas
 * (máximo 20 páginas); lo que no aparezca se queda sin dato y la celda lo dice.
 */
export function useIndice(base: string, recurso: Recurso, ids: unknown[]): { filas: Record<string, Row>; buscando: boolean } {
  const clave = base + '/' + recurso;
  const buscados = [...new Set(ids.filter((x): x is string => typeof x === 'string' && !!x))].sort();
  const firma = buscados.join(',');
  const [, setVersion] = useState(0);
  const [buscando, setBuscando] = useState(false);
  useEffect(() => {
    const cache = memoria.get(clave) ?? new Map<string, Row>();
    memoria.set(clave, cache);
    const faltan = new Set(buscados.filter((id) => !cache.has(id)));
    if (!faltan.size) return;
    let activo = true;
    const controller = new AbortController();
    setBuscando(true);
    (async () => {
      for (let pagina = 1; pagina <= 20 && faltan.size; pagina++) {
        const { data } = await request<Page>(`${base}/${recurso}?pagina=${pagina}&tamano=100`, { signal: controller.signal });
        for (const r of data.elementos) {
          if (!r.id) continue;
          cache.set(String(r.id), r);
          faltan.delete(String(r.id));
        }
        if (pagina * data.tamano >= data.total) break;
      }
    })()
      .catch(() => undefined)
      .finally(() => {
        if (!activo) return;
        setBuscando(false);
        setVersion((n) => n + 1);
      });
    return () => {
      activo = false;
      controller.abort();
    };
  }, [clave, firma]);
  const cache = memoria.get(clave);
  const filas: Record<string, Row> = {};
  for (const id of buscados) {
    const r = cache?.get(id);
    if (r) filas[id] = r;
  }
  return { filas, buscando };
}

/** Lo escrito en «Buscar»: un folio completo (C-2026-000007) se traduce a la referencia de su operación, que el servidor sí busca. */
export async function folioAReferencia(base: string, q: string): Promise<string> {
  if (!/^[CV]-\d{4}-\d{1,6}$/i.test(q)) return q;
  const { data } = await request<Page>(base + '/operaciones?' + new URLSearchParams({ q, pagina: '1', tamano: '5' }));
  const op = data.elementos.find((o) => String(o.folio).toUpperCase() === q.toUpperCase());
  return op?.id ? String(op.id) : q;
}

// ───────────────────────── celdas ─────────────────────────
/** Dinero que entra (te deben, te pagaron) o sale (debes, pagaste): flecha que baja a la libreta o sube de ella. */
function Sentido({ entra, children }: { entra: boolean; children: ReactNode }) {
  return (
    <span className="sentido" data-sentido={entra ? 'entra' : 'sale'}>
      <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" focusable="false">
        {entra ? <path d="M8 2.5v7.5M4.8 6.8 8 10l3.2-3.2M3 13.5h10" /> : <path d="M8 10.5V3M4.8 6.2 8 3l3.2 3.2M3 13.5h10" />}
      </svg>
      {children}
    </span>
  );
}
export const QuienDebe = ({ direccion }: { direccion: unknown }) => <Sentido entra={direccion === 'POR_COBRAR'}>{quienDebe(direccion)}</Sentido>;

/** Folio del trato con su tipo (compra/venta). Mientras se busca, lo dice; si no aparece, también. */
function Folio({ op, buscando }: { op?: Row; buscando: boolean }) {
  if (!op) return <span className="folio-celda"><span className="nil">{buscando ? 'Buscando folio…' : 'Sin folio'}</span></span>;
  return (
    <span className="folio-celda">
      <strong className="mono">{text(op.folio)}</strong>
      <small>{palabra(op.tipo)}</small>
    </span>
  );
}
const folioDe = (op?: Row) => (op ? text(op.folio) : 'sin folio');

/** Saldo de la cuenta; si ya cambió respecto del total del cierre, el total va debajo en chico (nunca la misma cifra dos veces). */
function Saldo({ saldo, total }: { saldo: unknown; total?: unknown }) {
  return (
    <span className="saldo-celda">
      <strong>{dinero(saldo)}</strong>
      {total !== undefined && !mismoImporte(saldo, total) && <small>de {dinero(total)}</small>}
    </span>
  );
}
function Vence({ el, dias }: { el: unknown; dias?: unknown }) {
  if (typeof el !== 'string' || !el) return <span className="muted">Sin fecha</span>;
  const n = typeof dias === 'number' ? dias : 0;
  return (
    <span className="vence-celda">
      <time dateTime={el}>{fecha(el)}</time>
      {n > 0 && <small>hace {n} {n === 1 ? 'día' : 'días'}</small>}
    </span>
  );
}
function EstadoDe({ l }: { l: Row }) {
  const e = estadoCuenta(l, today());
  return <Estado tono={e.tono}>{e.palabra}</Estado>;
}

// ───────────────────────── tablas ─────────────────────────
type Go = (next: string, row?: Row) => void;

/** Cuentas (liquidaciones) con su folio, contraparte y quién debe. `filas` vienen del listado de liquidaciones. */
export function TablaCuentas({ base, filas, onSelect, conEstado = true, etiqueta = 'Cuentas de la sede' }: { base: string; filas: Row[]; onSelect: (row: Row) => void; conEstado?: boolean; etiqueta?: string }) {
  const ops = useIndice(base, 'operaciones', filas.map((l) => l.operacion_id));
  const columnas: Columna[] = [
    { key: 'folio', label: 'Trato', render: (l) => <Folio op={ops.filas[String(l.operacion_id)]} buscando={ops.buscando} /> },
    { key: 'contraparte', label: 'Contraparte', render: (l) => text(l.snapshot_contraparte_nombre) },
    { key: 'direccion', label: 'Quién debe', render: (l) => <QuienDebe direccion={l.direccion} /> },
    { key: 'saldo', label: 'Saldo', money: true, render: (l) => <Saldo saldo={l.saldo} total={l.total} /> },
    ...(conEstado ? [{ key: 'estado', label: 'Estado', render: (l: Row) => <EstadoDe l={l} /> }] : []),
    { key: 'vence_el', label: 'Vence', render: (l) => <Vence el={l.vence_el} /> },
    { key: 'id', label: 'Ref. interna', ref: true },
  ];
  return (
    <DataTable
      rows={filas}
      columns={columnas}
      onSelect={onSelect}
      abrirEn="folio"
      nombre={(l) => 'liquidación ' + folioDe(ops.filas[String(l.operacion_id)])}
      etiqueta={etiqueta}
      clase="cuentas"
    />
  );
}

/** Pantalla Liquidaciones: todas las cuentas que dejaron los tratos cerrados. */
export function ListaLiquidaciones({ base, go }: { base: string; go: Go }) {
  return (
    <List
      path={base + '/liquidaciones'}
      etiquetaBusqueda="Buscar por folio o contraparte"
      buscar={(q) => folioAReferencia(base, q)}
      vacio={{ titulo: 'Todavía no hay cuentas', texto: 'Cada trato que cierres deja aquí su cuenta: lo que te deben o lo que debes.' }}
      render={(filas) => <TablaCuentas base={base} filas={filas} onSelect={(l) => go('liquidaciones', l)} />}
    />
  );
}

/**
 * Renglones de Cartera (solo traen liquidación, contraparte, saldo y vencimiento): la dirección y el total salen del
 * listado de liquidaciones y el folio del de operaciones.
 */
export function TablaCartera({ base, filas, go }: { base: string; filas: Row[]; go: Go }) {
  const liqs = useIndice(base, 'liquidaciones', filas.map((f) => f.liquidacion_id));
  const ops = useIndice(base, 'operaciones', Object.values(liqs.filas).map((l) => l.operacion_id));
  const liq = (f: Row) => liqs.filas[String(f.liquidacion_id)];
  const op = (f: Row) => ops.filas[String(liq(f)?.operacion_id)];
  const columnas: Columna[] = [
    { key: 'folio', label: 'Trato', render: (f) => <Folio op={op(f)} buscando={liqs.buscando || ops.buscando} /> },
    { key: 'contraparte', label: 'Contraparte' },
    { key: 'direccion', label: 'Quién debe', render: (f) => (liq(f) ? <QuienDebe direccion={liq(f)!.direccion} /> : <span className="nil">Buscando…</span>) },
    { key: 'saldo', label: 'Saldo', money: true, render: (f) => <Saldo saldo={f.saldo} total={liq(f)?.total} /> },
    { key: 'vence_el', label: 'Vence', render: (f) => <Vence el={f.vence_el} dias={f.dias_vencida} /> },
    { key: 'liquidacion_id', label: 'Ref. interna', ref: true },
  ];
  return (
    <DataTable
      rows={filas}
      columns={columnas}
      onSelect={(f) => go('liquidaciones', { id: String(f.liquidacion_id) })}
      abrirEn="folio"
      nombre={(f) => 'liquidación ' + folioDe(op(f))}
      etiqueta="Saldos pendientes"
      clase="cuentas"
    />
  );
}

/** Dinero registrado (cobros y pagos) por fecha, contraparte y sentido; lo que falta aplicar a una cuenta. */
export function ListaPagos({ base, revision, onSelect }: { base: string; revision: number; onSelect: (row: Row) => void }) {
  return (
    <List
      path={base + '/pagos'}
      revision={revision}
      etiquetaBusqueda="Buscar por contraparte o referencia"
      filters={[
        { name: 'estado', label: 'Estado del pago', options: ['REGISTRADO', 'VALIDADO'] },
        { name: 'tipo', label: 'Sentido del dinero', options: ['COBRO', 'PAGO'] },
      ]}
      vacio={{ titulo: 'Todavía no hay dinero apuntado', texto: 'Cada cobro o pago que apuntes aparece aquí para validarlo y abonarlo a su cuenta.' }}
      render={(filas) => <TablaPagos base={base} filas={filas} onSelect={onSelect} />}
    />
  );
}
function TablaPagos({ base, filas, onSelect }: { base: string; filas: Row[]; onSelect: (row: Row) => void }) {
  const partes = useIndice(base, 'contrapartes', filas.map((p) => p.parte_id));
  const nombre = (p: Row) => (partes.filas[String(p.parte_id)] ? text(partes.filas[String(p.parte_id)].nombre) : undefined);
  const columnas: Columna[] = [
    {
      key: 'recibido_el',
      label: 'Fecha',
      render: (p) => (
        <span className="fecha-celda">
          <strong>{fecha(p.recibido_el)}</strong>
          <small>{palabra(p.metodo)}</small>
        </span>
      ),
    },
    { key: 'parte', label: 'Contraparte', render: (p) => nombre(p) ?? <span className="nil">{partes.buscando ? 'Buscando…' : 'Sin nombre'}</span> },
    {
      key: 'tipo',
      label: 'Movimiento',
      render: (p) => (
        <span className="movimiento-celda">
          <Sentido entra={p.tipo === 'COBRO'}>{sentidoPago(p.tipo)}</Sentido>
          {p.naturaleza === 'REEMBOLSO' && <small>Reembolso</small>}
        </span>
      ),
    },
    { key: 'importe', label: 'Importe', money: true, render: (p) => dinero(p.importe) },
    { key: 'disponible', label: 'Por aplicar', money: true, render: (p) => <span className={conImporte(p.disponible) ? '' : 'cero'}>{dinero(p.disponible)}</span> },
    { key: 'estado', label: 'Estado' },
    { key: 'id', label: 'Ref. interna', ref: true },
  ];
  return (
    <DataTable
      rows={filas}
      columns={columnas}
      onSelect={onSelect}
      abrirEn="recibido_el"
      nombre={(p) => `${palabra(p.tipo).toLowerCase()} del ${fecha(p.recibido_el)}${nombre(p) ? ', ' + nombre(p) : ''}`}
      etiqueta="Dinero registrado"
      clase="cuentas"
    />
  );
}

/** Desglose del cierre en palabras: concepto, cantidad con su unidad, precio pactado e importe del servidor. */
export function TablaConceptos({ conceptos }: { conceptos: Row[] }) {
  const columnas: Columna[] = [
    {
      key: 'tipo',
      label: 'Concepto',
      render: (c) => (
        <span className="concepto-celda">
          <strong>{c.descripcion ? text(c.descripcion) : palabra(c.tipo)}</strong>
          {c.numero_lote !== undefined && c.numero_lote !== null && <small>Lote {text(c.numero_lote)}</small>}
        </span>
      ),
    },
    { key: 'cantidad', label: 'Cantidad', numeric: true, render: (c) => (c.unidad === 'MXN' ? <span className="muted">Importe fijo</span> : cantidad(c.cantidad, c.unidad)) },
    { key: 'precio_unitario', label: 'Precio', numeric: true, render: (c) => (c.precio_unitario === undefined || c.precio_unitario === null ? <span className="muted">No aplica</span> : precio(c.precio_unitario, c.unidad)) },
    { key: 'importe', label: 'Importe', money: true, render: (c) => dinero(c.importe) },
  ];
  return <DataTable rows={conceptos} columns={columnas} etiqueta="Desglose del cierre" />;
}
