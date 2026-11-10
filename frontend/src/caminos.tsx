// Caminos guiados (2026-11-09): cada proceso del negocio, una pregunta por paso.
// No hay atajos de negocio en el navegador: cada paso usa los mismos comandos que las pantallas completas
// (CommandForm conserva Idempotency-Key, If-Match y el reintento con la misma clave) y ningún total se calcula aquí;
// el total del trato lo da el simulador del servidor y el saldo lo da la liquidación.
import { useEffect, useRef, useState, type ReactNode } from "react";
import { request } from "./api";
import { type Page, type Row, type Sede, canonicalDecimal, money, text, today } from "./domain";
import { agrupar, cantidad, fecha, fechaHora as fechaYHora, importe, kilos, precio } from "./formato";
import { palabra } from "./palabras";
import { Amount, AvisosContexto, CommandForm, Field, Notice } from "./ui";
import { operationAnimals, replaceLot } from "./workflow";
import { Arete, Bascula, CamionJaula, Cebu, EscenaCamino, Fierro, Libreta, MiniPago, PuertaCorral } from "./escenas";

type Go = (next: string, row?: Row) => void;
const ESCRIBE = ["ADMIN", "OPERADOR"];
const COBRA = ["ADMIN", "CAJA"];

export const CAMINOS = [
  {
    id: "camino-compra",
    titulo: "Comprar ganado",
    desc: "Apunta el trato con quien te vende: qué cabezas, a cómo y cuándo llegan.",
    quien: "operador",
    roles: ESCRIBE,
    grande: true,
  },
  {
    id: "camino-venta",
    titulo: "Vender ganado",
    desc: "Aparta cabezas de tu corral, pacta el precio y cierra la venta.",
    quien: "operador",
    roles: ESCRIBE,
    grande: true,
  },
  { id: "camino-recibir", titulo: "Recibir en el corral", desc: "Marca las cabezas que ya llegaron de una compra.", quien: "operador", roles: ESCRIBE },
  { id: "camino-entregar", titulo: "Entregar ganado", desc: "Marca las cabezas que ya salieron con el comprador.", quien: "operador", roles: ESCRIBE },
  { id: "camino-cobro", titulo: "Cobrar o pagar", desc: "Apunta el dinero que entró o salió y abónalo a la cuenta correcta.", quien: "caja", roles: COBRA },
];

// ───────────────────────── utilidades ─────────────────────────
const str = (f: FormData, name: string) => String(f.get(name) || "");
const cash = (value: string) => ({ importe: canonicalDecimal(value, 2), moneda: "MXN" });
const importeDe = (m: unknown) => (m && typeof m === "object" && "importe" in m ? String((m as { importe: unknown }).importe) : "");
/** Centavos exactos (BigInt) para comparar importes del servidor; nunca se usan para calcular totales. */
function centavos(value: string): bigint | undefined {
  if (!/^-?\d+(?:\.\d+)?$/.test(value)) return undefined;
  const [whole, fraction = ""] = value.replace("-", "").split(".");
  const c = BigInt(whole + (fraction + "00").slice(0, 2));
  return value.startsWith("-") ? -c : c;
}
const conSaldo = (m: unknown) => (centavos(importeDe(m)) ?? 0n) > 0n;
/** Fechas con el formateador único (formato.ts); aquí en minúsculas porque van dentro de una frase. */
const fechaLarga = (iso: unknown) => fecha(iso, "sin fecha");
const fechaHora = (iso: unknown) => fechaYHora(iso, "sin fecha");
function localDentroDe(dias = 0) {
  const d = new Date(Date.now() + dias * 86400000);
  d.setSeconds(0, 0);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}
const arete = (r: Row) =>
  text(
    r.identificacion ||
      (Array.isArray(r.identificaciones) && r.identificaciones.length ? (r.identificaciones as Row[])[0].codigo_declarado : undefined) ||
      "Sin arete",
  );

/** Como useResource, pero sin consulta cuando no hay ruta y conservando el dato anterior mientras recarga. */
function useConsulta<T>(path: string | undefined, revision = 0) {
  const [state, setState] = useState<{ data?: T; etag?: string; loading: boolean; error?: Error }>({ loading: !!path });
  useEffect(() => {
    if (!path) {
      setState({ loading: false });
      return;
    }
    let active = true;
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: undefined }));
    request<T>(path, { signal: controller.signal })
      .then((r) => {
        if (active) setState({ data: r.data, etag: r.etag || undefined, loading: false });
      })
      .catch((error) => {
        if (active) setState({ loading: false, error });
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [path, revision]);
  return state;
}

function Campo({
  name,
  label,
  initial = "",
  required = true,
  type = "text",
  help,
  options,
  onValue,
}: {
  name: string;
  label: string;
  initial?: string;
  required?: boolean;
  type?: string;
  help?: string;
  options?: { value: string; label: string }[];
  onValue?: (v: string) => void;
}) {
  const [value, setValue] = useState(initial);
  return (
    <Field
      {...{ name, label, required, type, help, options, value }}
      onChange={(v) => {
        setValue(v);
        onValue?.(v);
      }}
    />
  );
}

function Opciones({
  name,
  legend,
  value,
  onChange,
  options,
}: {
  name: string;
  legend: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; titulo: string; hint?: string; escena?: ReactNode }[];
}) {
  return (
    <fieldset className="opciones">
      <legend>{legend}</legend>
      {options.map((o) => (
        <label className="opcion" key={o.value}>
          <input type="radio" name={name} value={o.value} checked={value === o.value} onChange={() => onChange(o.value)} />
          {o.escena}
          <strong>{o.titulo}</strong>
          {o.hint && <small>{o.hint}</small>}
        </label>
      ))}
    </fieldset>
  );
}

function Rail({
  titulo,
  subtitulo,
  pasos,
  actual,
  alcanzado,
  onPick,
  fijos = [],
  omitidos = [],
  notas = {},
}: {
  titulo: string;
  subtitulo: string;
  pasos: [string, string][];
  actual: string;
  alcanzado: string;
  onPick: (id: string) => void;
  /** Pasos ya superados a los que no se puede volver (p. ej. crear otro borrador). */
  fijos?: string[];
  /** Pasos que este trato no necesita (la báscula en un precio por cabeza). Se quedan en la ruta para que la cuenta no cambie. */
  omitidos?: string[];
  notas?: Record<string, string>;
}) {
  const tope = pasos.findIndex(([id]) => id === alcanzado);
  return (
    <aside className="rail">
      <h2>{titulo}</h2>
      <p>{subtitulo}</p>
      <nav aria-label="Pasos del camino">
        <ol>
          {pasos.map(([id, label], i) => (
            <li
              key={id}
              data-estado={id === actual ? "actual" : omitidos.includes(id) ? "omitido" : i < tope ? "hecho" : "pendiente"}
            >
              <button
                type="button"
                disabled={(omitidos.includes(id) && id !== actual) || i > tope || (fijos.includes(id) && id !== actual)}
                aria-current={id === actual ? "step" : undefined}
                onClick={() => onPick(id)}
              >
                <span className="num">{i + 1}</span>
                <span className="paso-nombre">
                  {label}
                  {notas[id] && <small className="nota-paso">{notas[id]}</small>}
                </span>
              </button>
            </li>
          ))}
        </ol>
      </nav>
    </aside>
  );
}

function Paso({
  eyebrow,
  pregunta,
  explica,
  escena,
  tecnico,
  children,
}: {
  eyebrow: string;
  pregunta: string;
  explica?: ReactNode;
  escena?: ReactNode;
  tecnico?: ReactNode;
  children?: ReactNode;
}) {
  const ref = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    ref.current?.focus({ preventScroll: false });
  }, [pregunta]);
  return (
    <section className="paso" aria-labelledby="paso-pregunta">
      <p className="sr-only">{eyebrow}</p>
      <h2 className="pregunta" id="paso-pregunta" tabIndex={-1} ref={ref}>
        {pregunta}
      </h2>
      {explica && <p className="explica">{explica}</p>}
      {escena && <div className="paso-escena">{escena}</div>}
      {children}
      {tecnico && (
        <details className="por-dentro">
          <summary>¿Qué pasa por dentro?</summary>
          <div className="tecnico">{tecnico}</div>
        </details>
      )}
    </section>
  );
}

/** Periodo contable y fecha de reconocimiento con un valor por defecto que el servidor acepta. */
function Contable({ base, verbo = "Se apunta en" }: { base: string; verbo?: string }) {
  const r = useConsulta<Page>(base + "/periodos?pagina=1&tamano=100");
  const hoy = today();
  const abiertos = (r.data?.elementos || []).filter((p) => p.estado === "ABIERTO");
  const cubre = (p: Row) => String(p.desde || "") <= hoy && (!p.hasta || hoy <= String(p.hasta));
  const dentro = abiertos.find(cubre);
  const elegido = dentro || [...abiertos].sort((a, b) => String(b.hasta || "").localeCompare(String(a.hasta || "")))[0];
  const sugerida = dentro ? hoy : elegido ? (hoy > String(elegido.hasta) ? String(elegido.hasta) : String(elegido.desde)) : hoy;
  const [cambiar, setCambiar] = useState(false);
  const [periodo, setPeriodo] = useState("");
  const [fecha, setFecha] = useState("");
  useEffect(() => {
    if (elegido) {
      setPeriodo(String(elegido.id));
      setFecha(sugerida);
    }
  }, [elegido?.id, sugerida]);
  const nombre = (p: Row) => (p.nombre ? text(p.nombre) : `del ${fechaLarga(p.desde)} al ${p.hasta ? fechaLarga(p.hasta) : "cierre"}`);
  if (r.loading && !r.data) return <p role="status">Buscando el periodo abierto…</p>;
  if (r.error) return <Notice error={r.error} />;
  if (!elegido)
    return <p className="notice error">No hay ningún periodo abierto en esta sede. El administrador lo abre en Control → Periodos.</p>;
  return (
    <>
      <div className="contable">
        <span>
          {verbo} el periodo <strong>{nombre(elegido)}</strong> con fecha <strong>{fechaLarga(fecha)}</strong>.
          {!dentro && (
            <>
              <br />
              <small>
                Hoy ({fechaLarga(hoy)}) no cae en ningún periodo abierto, por eso te propongo esa fecha. Si el movimiento es de este mes,
                el administrador abre el periodo en Control → Periodos.
              </small>
            </>
          )}
        </span>
        <button type="button" className="text-button" onClick={() => setCambiar((v) => !v)}>
          {cambiar ? "Listo" : "Cambiar"}
        </button>
      </div>
      {cambiar ? (
        <div className="form-grid">
          <Field
            name="periodo_id"
            label="Periodo"
            value={periodo}
            onChange={setPeriodo}
            options={abiertos.map((p) => ({ value: String(p.id), label: nombre(p) }))}
          />
          <Field name="fecha_reconocimiento" label="Fecha" type="date" value={fecha} onChange={setFecha} />
        </div>
      ) : (
        <>
          <input type="hidden" name="periodo_id" value={periodo} />
          <input type="hidden" name="fecha_reconocimiento" value={fecha} />
        </>
      )}
    </>
  );
}

function Siguiente({ titulo, detalle, onClick }: { titulo: string; detalle: string; onClick: () => void }) {
  return (
    <button type="button" className="siguiente" onClick={onClick}>
      <span>
        <strong>{titulo}</strong>
        <small>{detalle}</small>
      </span>
    </button>
  );
}

// ───────────────────────── Mesa de tratos ─────────────────────────
export function Mesa({ base, sede, go, startTour }: { base: string; sede: Sede; go: Go; startTour: () => void }) {
  const escribe = sede.roles.some((r) => ESCRIBE.includes(r));
  const borradores = useConsulta<Page>(escribe ? base + "/operaciones?pagina=1&tamano=5&estado=BORRADOR" : undefined);
  const acordadas = useConsulta<Page>(escribe ? base + "/operaciones?pagina=1&tamano=5&estado=ACORDADA" : undefined);
  const abiertos = [...(acordadas.data?.elementos || []), ...(borradores.data?.elementos || [])];
  return (
    <section className="mesa" aria-labelledby="mesa-titulo">
      <div className="mesa-head">
        <div>
                    <h2 id="mesa-titulo">¿Qué vas a hacer hoy?</h2>
        </div>
        <p>
          Elige y te llevo paso a paso.{" "}
          <button type="button" className="text-button" onClick={startTour}>
            Recorrido con voz (2 min)
          </button>
        </p>
      </div>
      <div className="mesa-grid">
        {CAMINOS.map((c) => {
          const puede = sede.roles.some((r) => c.roles.includes(r));
          return (
            <button
              key={c.id}
              type="button"
              className={"tarjeta-camino" + (c.grande ? " grande" : "")}
              data-camino={c.id}
              disabled={!puede}
              onClick={() => go(c.id)}
            >
              <span className="ilustracion" aria-hidden="true">
                <EscenaCamino id={c.id} />
              </span>
              <span className="texto">
                <strong>{c.titulo}</strong>
                <span className="desc">{c.desc}</span>
                <span className="quien">{puede ? "Empezar →" : (c.quien === "caja" ? "Esto lo registra caja" : "Esto lo registra el operador") + "; tu rol solo consulta"}</span>
              </span>
            </button>
          );
        })}
      </div>
      {abiertos.length > 0 && (
        <div className="pendientes-trato">
          <h3>Tratos a medio camino</h3>
          <ul>
            {abiertos.map((o) => (
              <li key={String(o.id)}>
                <span>
                  <span className="folio">{text(o.folio)}</span> · {o.tipo === "VENTA" ? "venta a" : "compra a"} {text(o.contraparte)}{" "}
                  <span className="badge" data-tone={o.estado === "ACORDADA" ? "progress" : "attention"}>
                    {o.estado === "ACORDADA" ? "Falta cerrar" : "Borrador"}
                  </span>
                </span>
                <button type="button" className="secondary" onClick={() => go(o.tipo === "VENTA" ? "camino-venta" : "camino-compra", o)}>
                  Continuar <span className="sr-only">{text(o.folio)}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

// ───────────────────────── Comprar / vender ─────────────────────────
type PasoTrato = "quien" | "ganado" | "precio" | "apartar" | "bascula" | "revisar" | "cerrar" | "listo";
const ACTIVAS = ["PENDIENTE_RECEPCION", "DISPONIBLE", "VENDIDA_PENDIENTE_ENTREGA"];

export function CaminoTrato({ base, sede, tipo, id, go }: { base: string; sede: Sede; tipo: "COMPRA" | "VENTA"; id?: string; go: Go }) {
  const venta = tipo === "VENTA";
  const ruta = venta ? "camino-venta" : "camino-compra";
  const escribe = sede.roles.some((r) => ESCRIBE.includes(r));
  const path = id ? base + "/operaciones/" + id : undefined;
  const [rev, setRev] = useState(0);
  const [vista, setVista] = useState<PasoTrato>();
  const [justo, setJusto] = useState(false);
  const bump = () => {
    setVista(undefined);
    setRev((n) => n + 1);
  };
  const op = useConsulta<Row>(path, rev);
  const posiciones = useConsulta<Page>(base + "/inventario/posiciones?pagina=1&tamano=100", rev);
  const o = op.data;
  const lotes = (o?.lotes as Row[] | undefined) || [];
  const lote = lotes.find((l) => Number(l.numero_lote) === 1) || lotes[0];
  const cabezas = ((venta ? lote?.posiciones : lote?.animales) as string[] | undefined) || [];
  const kg = lote?.unidad_precio === "KG";
  // El servidor apunta pesaje_base_id al ticket recién apuntado (PROPUESTA): solo cuenta como base cuando está APROBADO.
  const tickets = ((o?.pesajes as Row[] | undefined) || []).filter((t) => Number(t.numero_lote) === Number(lote?.numero_lote || 1));
  const ticketBase = tickets.find((t) => t.id === lote?.pesaje_base_id);
  const pesajeListo = ticketBase?.estado === "APROBADO";
  const ticketPendiente = ticketBase && !pesajeListo ? ticketBase : tickets.find((t) => t.estado === "PROPUESTA");
  const pos = posiciones.data?.elementos || [];
  const reservadas = venta && cabezas.length > 0 && cabezas.every((p) => pos.find((x) => x.id === p)?.reservada === true);
  const [sel, setSel] = useState<string[]>([]);
  useEffect(() => setSel(cabezas), [o?.id, rev, cabezas.join(",")]);

  let derivado: PasoTrato = "quien";
  if (o) {
    if (["CONFIRMADA", "CANCELADA", "ANULADA"].includes(String(o.estado))) derivado = "listo";
    else if (!cabezas.length) derivado = "ganado";
    else if (venta && !reservadas) derivado = "apartar";
    else if (o.estado === "BORRADOR" && kg && !pesajeListo) derivado = "bascula";
    else if (o.estado === "BORRADOR") derivado = "revisar";
    else derivado = "cerrar";
  }
  const actual = vista || derivado;
  const pasos: [PasoTrato, string][] = [
    ["quien", "Con quién"],
    ["ganado", "Qué cabezas"],
    ["precio", "A cómo"],
    ...(venta ? ([["apartar", "Apartar"]] as [PasoTrato, string][]) : []),
    // La báscula siempre está en la ruta: así la cuenta de pasos no cambia al elegir «por kilo».
    ["bascula", "Báscula"],
    ["revisar", "Revisar y aceptar"],
    ["cerrar", venta ? "Cerrar la venta" : "Cerrar el trato"],
    ["listo", "Listo"],
  ];
  const editable = !o || o.estado === "BORRADOR";
  const etag = op.etag || (o ? `"${String(o.version_lock)}"` : undefined);
  const omitidos = kg ? [] : ["bascula"];
  const notas: Record<string, string> = kg ? {} : { bascula: lote?.unidad_precio ? "No aplica: es por cabeza" : "Solo si es por kilo" };
  // A dónde llevan los botones de los avisos de error y qué folio nombrar si falta aprobar un ticket.
  const avisos = {
    acciones: {
      recargar: bump,
      ...(editable && o
        ? {
            bascula: () => {
              setRev((n) => n + 1);
              setVista(kg ? "bascula" : "precio");
            },
            precio: () => setVista("precio"),
            ganado: () => setVista("ganado"),
          }
        : {}),
    },
    datos: { folio_ticket: ticketPendiente?.ticket_folio ? String(ticketPendiente.ticket_folio) : undefined },
  };
  const requiereRecepcion =
    o?.requiere_recepcion === true ||
    ((o?.contratos as Row[] | undefined) || []).some((c) => c.numero_version === o?.numero_version_actual && c.requiere_recepcion === true);

  if (!escribe)
    return (
      <section className="paso">
        <h2 className="pregunta">Este camino lo hace el operador</h2>
        <p className="explica">Tu rol en {sede.nombre} es de consulta o de caja. Puedes revisar el trato en Expediente o en Liquidaciones.</p>
      </section>
    );
  if (id && op.loading && !o) return <p role="status">Abriendo el trato…</p>;
  if (op.error && !o) return <Notice error={op.error} />;

  return (
    <AvisosContexto.Provider value={avisos}>
    <div className="camino">
      <Rail
        titulo={venta ? "Vender ganado" : "Comprar ganado"}
        subtitulo={o ? `${text(o.folio)} · ${text(o.contraparte)}` : "Un trato nuevo"}
        pasos={pasos}
        actual={actual}
        alcanzado={derivado}
        fijos={!o ? [] : o.estado === "BORRADOR" ? ["quien"] : pasos.map(([p]) => p).filter((p) => p !== derivado)}
        omitidos={omitidos}
        notas={notas}
        onPick={(p) => setVista(p === derivado ? undefined : (p as PasoTrato))}
      />
      <div>
        {lotes.length > 1 && (
          <p className="notice">
            Este trato tiene {lotes.length} lotes. El camino guiado trabaja con el lote 1;{" "}
            <button type="button" className="text-button" onClick={() => go("captura", o)}>
              ábrelo en la pantalla completa
            </button>{" "}
            para los demás.
          </p>
        )}
        {actual === "quien" && <PasoQuien base={base} venta={venta} ruta={ruta} go={go} />}
        {actual === "ganado" && o && (
          <PasoGanado base={base} venta={venta} sel={sel} setSel={setSel} posiciones={pos} rev={rev} onNext={() => setVista("precio")} />
        )}
        {actual === "precio" && o && path && editable && (
          <PasoPrecio venta={venta} path={path} etag={etag} o={o} lotes={lotes} lote={lote} sel={sel} requiereRecepcion={requiereRecepcion} onDone={bump} />
        )}
        {actual === "apartar" && o && path && <PasoApartar path={path} cabezas={cabezas} posiciones={pos} onDone={bump} />}
        {actual === "bascula" && o && path && lote && (
          <PasoBascula
            base={base}
            path={path}
            etag={etag}
            o={o}
            lote={lote}
            posiciones={pos}
            requiereRecepcion={requiereRecepcion}
            onDone={bump}
            onSeguir={() => setVista(undefined)}
          />
        )}
        {actual === "revisar" && o && path && (
          <PasoRevisar base={base} path={path} etag={etag} o={o} lote={lote} cabezas={cabezas} posiciones={pos} venta={venta} rev={rev} onDone={bump} onCambiar={() => setVista("precio")} />
        )}
        {actual === "cerrar" && o && path && (
          <PasoCerrar
            base={base}
            path={path}
            etag={etag}
            o={o}
            lote={lote}
            cabezas={cabezas}
            posiciones={pos}
            venta={venta}
            rev={rev}
            onDone={() => {
              setJusto(true);
              bump();
            }}
            onReabrir={bump}
          />
        )}
        {actual === "listo" && o && <PasoListo o={o} venta={venta} justo={justo} ruta={ruta} go={go} lote={lote} cabezas={cabezas} posiciones={pos} base={base} cobra={sede.roles.some((r) => COBRA.includes(r))} />}
        {(actual === "precio" || actual === "ganado") && o && !editable && (
          <p className="notice">Las condiciones ya se aceptaron. Para cambiarlas, reábrelas en el paso «Cerrar».</p>
        )}
      </div>
    </div>
    </AvisosContexto.Provider>
  );
}

function PasoQuien({ base, venta, ruta, go }: { base: string; venta: boolean; ruta: string; go: Go }) {
  const [query, setQuery] = useState("");
  const [buscar, setBuscar] = useState("");
  const [rev, setRev] = useState(0);
  const [parte, setParte] = useState("");
  const lista = useConsulta<Page>(base + "/contrapartes?pagina=1&tamano=50" + (buscar ? "&q=" + encodeURIComponent(buscar) : ""), rev);
  return (
    <Paso
      eyebrow="Paso 1 · Con quién"
      pregunta={venta ? "¿A quién le vendes?" : "¿A quién le compras?"}
      explica={
        venta
          ? "Elige al comprador. Si es la primera vez que le vendes, dalo de alta aquí mismo."
          : "Elige a quien te vende el ganado. Si es la primera vez que le compras, dalo de alta aquí mismo."
      }
      tecnico={
        <>
          Al empezar se crea la operación en estado <code>BORRADOR</code> con <code>bovi.cmd_ejecutar(…, 'crear_operacion')</code> en el
          nodo dueño de la sede (A o B). Un borrador no mueve inventario ni dinero: se puede corregir o cancelar.
        </>
      }
    >
      <form
        className="buscador"
        onSubmit={(e) => {
          e.preventDefault();
          setBuscar(query.trim());
        }}
      >
        <Field name="buscar_parte" label="Buscar por nombre" required={false} value={query} onChange={setQuery} />
        <button className="secondary">Buscar</button>
      </form>
      {lista.error && <Notice error={lista.error} />}
      <div className="renglones" role="radiogroup" aria-label={venta ? "Comprador" : "Vendedor"}>
        {(lista.data?.elementos || []).map((p) => (
          <label className="renglon" key={String(p.id)}>
            <input type="radio" name="parte_elegida" checked={parte === p.id} onChange={() => setParte(String(p.id))} />
            <span>
              <strong>{text(p.nombre)}</strong>
              <small>
                {p.tipo_persona === "MORAL" ? "Empresa" : "Persona"}
                {p.telefono ? " · " + text(p.telefono) : ""}
                {p.rfc ? " · RFC " + text(p.rfc) : ""}
              </small>
            </span>
          </label>
        ))}
        {lista.loading && !lista.data && (
          <p className="renglon" role="status">
            Buscando…
          </p>
        )}
        {lista.data && !lista.data.elementos.length && <p className="renglon">Nadie con ese nombre. Dalo de alta abajo.</p>}
      </div>
      <details className="alta-rapida">
        <summary>¿Es nuevo? Darlo de alta</summary>
        <CommandForm
          path={base + "/contrapartes"}
          label="Guardar y elegir"
          build={(f) => {
            const nombre = str(f, "nombre").trim();
            if (!nombre) throw new Error("Escribe el nombre completo o la razón social.");
            return { nombre, tipo_persona: str(f, "tipo_persona"), telefono: str(f, "telefono") || undefined };
          }}
          onDone={(r) => {
            setParte(String(r.id));
            setBuscar("");
            setQuery("");
            setRev((n) => n + 1);
          }}
        >
          <div className="form-grid">
            <Campo name="nombre" label="Nombre completo o razón social" />
            <Campo
              name="tipo_persona"
              label="Es"
              initial="FISICA"
              options={[
                { value: "FISICA", label: "Una persona" },
                { value: "MORAL", label: "Una empresa" },
              ]}
            />
            <Campo name="telefono" label="Teléfono" type="tel" required={false} />
          </div>
        </CommandForm>
      </details>
      <CommandForm
        path={base + "/operaciones"}
        label="Empezar el trato"
        build={(f) => {
          if (!parte) throw new Error(venta ? "Elige al comprador (o dalo de alta)." : "Elige a quien te vende (o dalo de alta).");
          return { tipo: venta ? "VENTA" : "COMPRA", parte_id: parte, fecha_operacion: str(f, "fecha_operacion"), requiere_recepcion: false };
        }}
        onDone={(r) => go(ruta, r)}
      >
        <div className="form-grid">
          <Campo name="fecha_operacion" label="¿Qué día fue el trato?" type="date" initial={today()} />
        </div>
      </CommandForm>
    </Paso>
  );
}

function PasoGanado({
  base,
  venta,
  sel,
  setSel,
  posiciones,
  rev,
  onNext,
}: {
  base: string;
  venta: boolean;
  sel: string[];
  setSel: (f: (c: string[]) => string[]) => void;
  posiciones: Row[];
  rev: number;
  onNext: () => void;
}) {
  const [query, setQuery] = useState("");
  const [buscar, setBuscar] = useState("");
  const [pagina, setPagina] = useState(1);
  const [altas, setAltas] = useState(0);
  const lista = useConsulta<Page>(
    base +
      (venta ? "/inventario/posiciones?estado=DISPONIBLE&" : "/animales?") +
      new URLSearchParams({ pagina: String(pagina), tamano: "40", ...(buscar ? { q: buscar } : {}) }),
    rev + altas,
  );
  const enCorral = new Set(posiciones.filter((p) => ACTIVAS.includes(String(p.estado))).map((p) => String(p.animal_id)));
  const motivo = (r: Row) =>
    venta
      ? r.reservada === true && !sel.includes(String(r.id))
        ? "Apartada en otro trato"
        : undefined
      : enCorral.has(String(r.id))
        ? "Ya está en tu inventario"
        : undefined;
  const filas = lista.data?.elementos || [];
  return (
    <Paso
      eyebrow="Paso 2 · Qué cabezas"
      pregunta={venta ? "¿Qué cabezas vendes?" : "¿Qué cabezas compras?"}
      explica={
        venta
          ? "Toca los aretes de los animales que salen en esta venta. Debajo de cada uno ves lo que te costó."
          : "Toca los aretes de los animales del trato. Si un animal todavía no está registrado, apunta su arete abajo."
      }
      tecnico={
        <>
          {venta ? (
            <>
              Se venden <strong>posiciones</strong> de inventario (un ciclo de tenencia de cada animal), no animales sueltos: así una vaca
              recomprada tiene su propio costo en cada ciclo.
            </>
          ) : (
            <>
              Cada animal tiene una identidad permanente (UUID) y uno o varios aretes. La base impide que un animal tenga dos ciclos activos
              a la vez (índice único parcial <code>uk_posicion_inventario_activo</code>).
            </>
          )}{" "}
          La selección se guarda junto con el precio en el siguiente paso.
        </>
      }
    >
      <form
        className="buscador"
        onSubmit={(e) => {
          e.preventDefault();
          setBuscar(query.trim());
          setPagina(1);
        }}
      >
        <Field name="buscar_arete" label="Buscar arete" required={false} value={query} onChange={setQuery} />
        <button className="secondary">Buscar</button>
      </form>
      {lista.error && <Notice error={lista.error} />}
      <div className="aretes" role="group" aria-label="Aretes">
        {filas.map((r) => {
          const no = motivo(r);
          const checked = sel.includes(String(r.id));
          return (
            <label className="arete-opcion" key={String(r.id)}>
              <input
                type="checkbox"
                checked={checked}
                disabled={!!no}
                onChange={(e) =>
                  setSel((c) => (e.target.checked ? [...new Set([...c, String(r.id)])] : c.filter((x) => x !== String(r.id))))
                }
              />
              <Arete code={arete(r)} selected={checked} muted={!!no} />
              <small>{no || (venta ? "Costó " + money(r.costo_vigente) : r.sexo === "H" ? "Hembra" : r.sexo === "M" ? "Macho" : "")}</small>
            </label>
          );
        })}
        {lista.loading && !lista.data && <p role="status">Buscando aretes…</p>}
        {lista.data && !filas.length && (
          <p className="notice">{venta ? "No hay cabezas disponibles para vender en esta sede." : "No hay aretes con esa búsqueda."}</p>
        )}
      </div>
      {lista.data && lista.data.total > 40 && (
        <div className="pagination">
          <span>
            {lista.data.total} aretes · página {pagina}
          </span>
          <div>
            <button type="button" className="secondary" disabled={pagina === 1} onClick={() => setPagina((p) => p - 1)}>
              Anterior
            </button>
            <button type="button" className="secondary" disabled={pagina * 40 >= lista.data.total} onClick={() => setPagina((p) => p + 1)}>
              Siguiente
            </button>
          </div>
        </div>
      )}
      {!venta && (
        <details className="alta-rapida" key={altas}>
          <summary>Apuntar un arete nuevo</summary>
          <CommandForm
            path={base + "/animales"}
            label="Registrar y agregar al trato"
            build={(f) => {
              const codigo = str(f, "codigo").trim();
              if (!codigo) throw new Error("Escribe el número del arete.");
              return { sexo: str(f, "sexo"), identificaciones: [{ sistema: str(f, "sistema"), codigo }] };
            }}
            onDone={(r) => {
              setSel((c) => [...new Set([...c, String(r.id)])]);
              setAltas((n) => n + 1);
            }}
          >
            <div className="form-grid">
              <Campo name="codigo" label="Número del arete" />
              <Campo
                name="sistema"
                label="Tipo de arete"
                initial="SINIIGA"
                options={[
                  { value: "SINIIGA", label: "SINIIGA (amarillo oficial)" },
                  { value: "INTERNO", label: "Interno del rancho" },
                  { value: "SINIDA", label: "SINIDA" },
                  { value: "OTRO", label: "Otro" },
                ]}
              />
              <Campo
                name="sexo"
                label="Sexo"
                options={[
                  { value: "M", label: "Macho" },
                  { value: "H", label: "Hembra" },
                ]}
              />
            </div>
          </CommandForm>
        </details>
      )}
      <p className="contador" role="status">
        {sel.length} {sel.length === 1 ? "cabeza elegida" : "cabezas elegidas"}
        {sel.length > filas.filter((r) => sel.includes(String(r.id))).length ? " (algunas en otra página o búsqueda)" : ""}
      </p>
      <div className="paso-acciones">
        <button type="button" className="primary" disabled={!sel.length} onClick={onNext}>
          Seguir: el precio
        </button>
      </div>
    </Paso>
  );
}

function PasoPrecio({
  venta,
  path,
  etag,
  o,
  lotes,
  lote,
  sel,
  requiereRecepcion,
  onDone,
}: {
  venta: boolean;
  path: string;
  etag?: string;
  o: Row;
  lotes: Row[];
  lote?: Row;
  sel: string[];
  requiereRecepcion: boolean;
  onDone: () => void;
}) {
  const [unidad, setUnidad] = useState(String(lote?.unidad_precio || "CABEZA"));
  const [llegada, setLlegada] = useState(requiereRecepcion ? "camino" : "corral");
  const extras = !!(lote && (conSaldo(lote.cargos_pactados) || conSaldo(lote.bonificaciones_pactadas)));
  return (
    <Paso
      eyebrow="Paso 3 · A cómo"
      pregunta="¿Cómo quedó el precio?"
      explica={`${sel.length} ${sel.length === 1 ? "cabeza" : "cabezas"} en este trato. Escribe lo que acordaron; el total lo calcula el sistema.`}
      tecnico={
        <>
          Se guarda con <code>PATCH /operaciones/{"{id}"}</code> (comando <code>editar_operacion</code>) usando la versión que tienes en
          pantalla (<code>If-Match</code>): si otra persona cambió el trato, el servidor responde 412 y te pide recargar. Solo se puede editar
          en <code>BORRADOR</code> (trigger <code>trg_borrador</code>). Una regla CHECK exige pesaje cuando el precio es por kilo y lo prohíbe
          cuando es por cabeza.
        </>
      }
    >
      <CommandForm
        path={path}
        method="PATCH"
        etag={etag}
        label="Guardar el precio"
        build={(f) => {
          const precio = str(f, "precio_unitario").trim();
          if (!precio) throw new Error(unidad === "KG" ? "Escribe a cómo quedó el kilo." : "Escribe a cómo quedó cada cabeza.");
          const otros = lotes.filter((l) => Number(l.numero_lote) !== Number(lote?.numero_lote || 1));
          return {
            lotes: replaceLot(otros, {
              numero_lote: Number(lote?.numero_lote || 1),
              ...(venta ? { posiciones: sel } : { animales: sel }),
              unidad_precio: unidad,
              precio_unitario: canonicalDecimal(precio, 4),
              pesaje_base_id: (unidad === "KG" && lote?.unidad_precio === "KG" && lote?.pesaje_base_id) || undefined,
              deduccion_pct: unidad === "KG" && str(f, "deduccion_pct") ? canonicalDecimal(str(f, "deduccion_pct"), 6) : undefined,
              cargos_pactados: str(f, "cargos_pactados") ? canonicalDecimal(str(f, "cargos_pactados"), 2) : undefined,
              bonificaciones_pactadas: str(f, "bonificaciones_pactadas") ? canonicalDecimal(str(f, "bonificaciones_pactadas"), 2) : undefined,
            }),
            requiere_recepcion: !venta && llegada === "camino",
          };
        }}
        onDone={onDone}
      >
        <Opciones
          name="unidad"
          legend="¿Cómo se paga?"
          value={unidad}
          onChange={setUnidad}
          options={[
            {
              value: "CABEZA",
              titulo: "Por cabeza",
              hint: "Un precio fijo por cada animal.",
              escena: (
                <svg viewBox="0 0 110 70" aria-hidden="true">
                  <Cebu x={2} y={2} s={1} />
                </svg>
              ),
            },
            {
              value: "KG",
              titulo: "Por kilo",
              hint: "Se pesa en báscula y se paga cada kilo.",
              escena: <Bascula kg="—" />,
            },
          ]}
        />
        <div className="form-grid">
          <Campo
            key={unidad}
            name="precio_unitario"
            label={unidad === "KG" ? "¿A cómo el kilo? (MXN)" : "¿A cómo cada cabeza? (MXN)"}
            initial={lote?.unidad_precio === unidad && lote?.precio_unitario ? String(lote.precio_unitario) : ""}
            help="Por ejemplo 52.50. Puedes escribirlo con $ o con comas; el total lo calcula el sistema."
          />
        </div>
        {!venta && (
          <Opciones
            name="llegada"
            legend="¿Dónde está el ganado?"
            value={llegada}
            onChange={setLlegada}
            options={[
              { value: "corral", titulo: "Ya está en mi corral", hint: "Entra al inventario como disponible al cerrar el trato." },
              { value: "camino", titulo: "Viene en camino", hint: "Al llegar lo marcas en «Recibir en el corral»." },
            ]}
          />
        )}
        <details className="alta-rapida" open={extras}>
          <summary>¿Hubo algo extra en el trato? (opcional)</summary>
          <div className="form-grid">
            <Campo
              name="cargos_pactados"
              label="Cargos que se suman (MXN)"
              required={false}
              initial={conSaldo(lote?.cargos_pactados) ? importeDe(lote?.cargos_pactados) : ""}
              help="Por ejemplo, el flete o la comisión que se acordó pagar aparte."
            />
            <Campo
              name="bonificaciones_pactadas"
              label="Descuentos que se restan (MXN)"
              required={false}
              initial={conSaldo(lote?.bonificaciones_pactadas) ? importeDe(lote?.bonificaciones_pactadas) : ""}
              help="Por ejemplo, una rebaja por un animal golpeado."
            />
            {unidad === "KG" && (
              <Campo
                name="deduccion_pct"
                label="Merma o destare pactado (%)"
                required={false}
                initial={lote?.deduccion_pct && String(lote.deduccion_pct) !== "0.000000" ? String(lote.deduccion_pct) : ""}
                help="Solo si lo acordaron. El sistema no descuenta mermas por su cuenta."
              />
            )}
          </div>
        </details>
      </CommandForm>
      <p className="muted">Trato {text(o.folio)}. Puedes volver a «Qué cabezas» desde la ruta de la izquierda.</p>
    </Paso>
  );
}

function PasoApartar({ path, cabezas, posiciones, onDone }: { path: string; cabezas: string[]; posiciones: Row[]; onDone: () => void }) {
  return (
    <Paso
      eyebrow="Paso 4 · Apartar"
      pregunta="Aparta las cabezas mientras cierras"
      explica="Mientras el trato se cierra, nadie más puede vender estas cabezas. Si el apartado vence, vuelven a quedar libres."
      tecnico={
        <>
          Comando <code>reservar_venta</code>: bloquea las posiciones con <code>SELECT … FOR UPDATE ORDER BY id</code>. Si dos personas apartan
          la misma cabeza al mismo tiempo, una gana y la otra recibe <code>BV402</code> (índice parcial + trigger{" "}
          <code>trg_reserva_activa_unica</code>, prueba TEST-10). El apartado dura como máximo 30 días.
        </>
      }
    >
      <div className="aretes chicos" aria-label="Cabezas a apartar">
        {cabezas.map((c) => (
          <Arete key={c} code={arete(posiciones.find((p) => p.id === c) || {})} selected />
        ))}
      </div>
      <CommandForm
        path={path + "/reservas"}
        label="Apartar estas cabezas"
        build={(f) => ({ posiciones: cabezas, vence_en: new Date(str(f, "vence_en")).toISOString() })}
        onDone={onDone}
      >
        <div className="form-grid">
          <Campo name="vence_en" label="¿Hasta cuándo las apartas?" type="datetime-local" initial={localDentroDe(3)} help="Te propongo 3 días." />
        </div>
      </CommandForm>
    </Paso>
  );
}

function condicionesDe(lote: Row) {
  return {
    numero_lote: Number(lote.numero_lote || 1),
    ...((lote.posiciones as string[] | undefined)?.length ? { posiciones: lote.posiciones } : { animales: lote.animales }),
    unidad_precio: lote.unidad_precio,
    precio_unitario: lote.precio_unitario,
    deduccion_pct: lote.deduccion_pct || undefined,
    cargos_pactados: conSaldo(lote.cargos_pactados) ? importeDe(lote.cargos_pactados) : undefined,
    bonificaciones_pactadas: conSaldo(lote.bonificaciones_pactadas) ? importeDe(lote.bonificaciones_pactadas) : undefined,
  };
}

function PasoBascula({
  base,
  path,
  etag,
  o,
  lote,
  posiciones,
  requiereRecepcion,
  onDone,
  onSeguir,
}: {
  base: string;
  path: string;
  etag?: string;
  o: Row;
  lote: Row;
  posiciones: Row[];
  requiereRecepcion: boolean;
  onDone: () => void;
  onSeguir: () => void;
}) {
  const [neto, setNeto] = useState("");
  const [recien, setRecien] = useState(false);
  const tickets = ((o.pesajes as Row[] | undefined) || []).filter((t) => Number(t.numero_lote) === Number(lote.numero_lote || 1));
  // Al apuntar un ticket el servidor ya lo deja como base del lote (PROPUESTA); falta que alguien lo apruebe.
  const referido = tickets.find((t) => t.id === lote.pesaje_base_id);
  const enUso = referido?.estado === "APROBADO" ? referido : undefined;
  const porAprobar = referido?.estado === "PROPUESTA" ? referido : undefined;
  const aprobadoSuelto = !enUso && !porAprobar ? tickets.find((t) => t.estado === "APROBADO") : undefined;
  const revisar = porAprobar || (!enUso && !aprobadoSuelto ? tickets.find((t) => t.estado === "PROPUESTA") : undefined);
  const kgDe = (t?: Row) => (t?.neto && typeof t.neto === "object" && "kg" in t.neto ? agrupar((t.neto as { kg: unknown }).kg, 3) ?? "" : "");
  const visible = enUso || revisar || aprobadoSuelto;
  const lectura = visible ? kgDe(visible) : neto || "0";
  const tecnico = (
    <>
      Dos comandos: <code>registrar_pesaje</code> guarda el ticket con la composición exacta del lote (y el servidor lo deja como{" "}
      <code>pesaje_base_id</code> del lote en estado <code>PROPUESTA</code>), y <code>aprobar_pesaje</code> lo congela (triggers{" "}
      <code>trg_aprobado</code> y <code>trg_pesaje_composicion</code>). Aceptar el trato exige que ese ticket esté <code>APROBADO</code>{" "}
      (RN-014). Un ticket aprobado no se edita: corregirlo crea otro y el original queda como CORREGIDO. Si dos pesajes del mismo grupo
      difieren, la diferencia se conserva pero <strong>no se descuenta sola</strong>.
    </>
  );
  const corregir = (
    <p className="muted">
      ¿No coincide con el papel? Corrígelo en Operaciones → Tickets y pesajes: se guarda una versión nueva y la anterior no se borra.
    </p>
  );
  return (
    <Paso
      eyebrow="Paso · Báscula"
      pregunta={enUso ? "Este peso ya es la base del precio" : revisar ? "¿El ticket dice esto?" : aprobadoSuelto ? "¿Usamos este peso?" : "¿Cuánto pesó el lote?"}
      explica={
        enUso
          ? "El ticket está aprobado y el trato ya lo usa para el precio por kilo."
          : revisar
            ? "Compáralo con el papel de la báscula. Si coincide, queda fijo y es la base del precio por kilo."
            : aprobadoSuelto
              ? "Este ticket ya está aprobado. Úsalo como base del precio por kilo."
              : "Copia los datos del ticket de la báscula. Pesa todas las cabezas del trato juntas."
      }
      escena={<Bascula kg={lectura} play={recien} />}
      tecnico={tecnico}
    >
      {visible && (
        <dl className="ticket-revisar" aria-label={"Ticket " + text(visible.ticket_folio)}>
          <div>
            <dt>Folio</dt>
            <dd>{text(visible.ticket_folio)}</dd>
          </div>
          <div>
            <dt>Peso neto</dt>
            <dd className="kg">{kgDe(visible)} kg</dd>
          </div>
          {visible.pesado_en ? (
            <div>
              <dt>Pesado</dt>
              <dd>{fechaHora(visible.pesado_en)}</dd>
            </div>
          ) : null}
        </dl>
      )}
      {enUso ? (
        <div className="paso-acciones">
          <button type="button" className="primary" onClick={onSeguir}>
            Seguir: revisar el trato
          </button>
        </div>
      ) : revisar ? (
        <CommandForm
          path={base + "/pesajes/" + revisar.id + "/aprobar"}
          label="Sí, usar este pesaje"
          exito={revisar.id === lote.pesaje_base_id ? "Pesaje aprobado: ya es la base del precio por kilo." : "Pesaje aprobado."}
          build={() => ({})}
          onDone={onDone}
        >
          {corregir}
        </CommandForm>
      ) : aprobadoSuelto ? (
        <CommandForm
          path={path}
          method="PATCH"
          etag={etag}
          label="Usar este peso en el trato"
          exito="Peso guardado como base del precio por kilo."
          build={() => ({
            lotes: replaceLot(
              ((o.lotes as Row[]) || []).filter((l) => Number(l.numero_lote) !== Number(lote.numero_lote || 1)),
              { ...condicionesDe(lote), pesaje_base_id: aprobadoSuelto.id },
            ),
            requiere_recepcion: o.tipo !== "VENTA" && requiereRecepcion,
          })}
          onDone={onDone}
        >
          <p className="muted">Se guarda en las condiciones del lote. El total lo calcula el sistema con este peso.</p>
        </CommandForm>
      ) : (
        <CommandForm
          path={path + "/pesajes"}
          label="Apuntar el pesaje"
          exito="Ticket apuntado. Ahora revísalo contra el papel."
          build={(f) => ({
            numero_lote: Number(lote.numero_lote || 1),
            modo: "NETO_REPORTADO",
            neto: { kg: canonicalDecimal(str(f, "neto"), 3) },
            pesado_en: new Date(str(f, "pesado_en")).toISOString(),
            ticket_folio: str(f, "ticket_folio").trim(),
            animales: operationAnimals({ ...o, lotes: [lote] }, posiciones).map((animal_id) => ({ animal_id })),
          })}
          onDone={() => {
            setRecien(true);
            onDone();
          }}
        >
          <div className="form-grid">
            <Campo name="neto" label="Peso neto del ticket (kg)" help="Lo que dice el ticket ya sin la tara, por ejemplo 4,520.5." onValue={setNeto} />
            <Campo name="ticket_folio" label="Folio del ticket" />
            <Campo name="pesado_en" label="Fecha y hora del pesaje" type="datetime-local" initial={localDentroDe(0)} />
          </div>
        </CommandForm>
      )}
    </Paso>
  );
}

function useEtiquetas(base: string, venta: boolean, cabezas: string[], posiciones: Row[]) {
  const [labels, setLabels] = useState<Record<string, string>>({});
  const clave = cabezas.join(",");
  useEffect(() => {
    if (venta) {
      setLabels(Object.fromEntries(cabezas.map((c) => [c, arete(posiciones.find((p) => p.id === c) || {})])));
      return;
    }
    let active = true;
    const controller = new AbortController();
    Promise.all(
      cabezas.map((id) =>
        request<Row>(base + "/animales/" + id, { signal: controller.signal })
          .then((r) => [id, arete(r.data)] as const)
          .catch(() => [id, "Sin arete"] as const),
      ),
    ).then((pairs) => {
      if (active) setLabels(Object.fromEntries(pairs));
    });
    return () => {
      active = false;
      controller.abort();
    };
  }, [base, venta, clave, posiciones.length]);
  return labels;
}

function NotaTrato({
  base,
  o,
  lote,
  cabezas,
  posiciones,
  venta,
  total,
  conceptos,
  marca,
}: {
  base: string;
  o: Row;
  lote?: Row;
  cabezas: string[];
  posiciones: Row[];
  venta: boolean;
  total?: unknown;
  conceptos?: Row[];
  marca?: ReactNode;
}) {
  const labels = useEtiquetas(base, venta, cabezas, posiciones);
  const ticket = ((o.pesajes as Row[] | undefined) || []).find((t) => t.id === lote?.pesaje_base_id);
  return (
    <article className={"nota-trato" + (marca ? " con-marca" : "")} aria-label="Nota del trato">
      {marca && <div className="marca-fierro">{marca}</div>}
      <header>
        <strong>{venta ? "Nota de venta" : "Nota de compra"}</strong>
        <span className="mono">{text(o.folio)}</span>
      </header>
      <dl>
        <dt>{venta ? "Comprador" : "Vendedor"}</dt>
        <dd>{text(o.contraparte)}</dd>
        <dt>Fecha del trato</dt>
        <dd>{fechaLarga(o.fecha_operacion)}</dd>
        <dt>Cabezas</dt>
        <dd>
          <span className="aretes chicos">
            {cabezas.map((c) => (
              <Arete key={c} code={labels[c] || "…"} selected />
            ))}
          </span>
        </dd>
        {lote && (
          <>
            <dt>Precio</dt>
            <dd className="mono">
              {precio(lote.precio_unitario, lote.unidad_precio)}
            </dd>
          </>
        )}
        {ticket && (
          <>
            <dt>Báscula</dt>
            <dd className="mono">
              Ticket {text(ticket.ticket_folio)} · {kilos(ticket.neto)}
            </dd>
          </>
        )}
        {lote && conSaldo(lote.cargos_pactados) && (
          <>
            <dt>Cargos</dt>
            <dd className="mono">+ {money(lote.cargos_pactados)}</dd>
          </>
        )}
        {lote && conSaldo(lote.bonificaciones_pactadas) && (
          <>
            <dt>Descuentos</dt>
            <dd className="mono">− {money(lote.bonificaciones_pactadas)}</dd>
          </>
        )}
      </dl>
      {conceptos && conceptos.length > 0 && (
        <ul className="lineas">
          {conceptos.map((c, i) => (
            <li key={i}>
              <span>
                {c.descripcion ? text(c.descripcion) : palabra(c.tipo)}
                {c.cantidad && c.unidad !== "MXN" ? " · " + cantidad(c.cantidad, c.unidad) : ""}
              </span>
              <span>{money(c.importe)}</span>
            </li>
          ))}
        </ul>
      )}
      {total !== undefined && (
        <div className="total">
          <span>Total que calcula el sistema</span>
          <strong>
            <Amount value={total} />
          </strong>
        </div>
      )}
    </article>
  );
}

function PasoRevisar({
  base,
  path,
  etag,
  o,
  lote,
  cabezas,
  posiciones,
  venta,
  rev,
  onDone,
  onCambiar,
}: {
  base: string;
  path: string;
  etag?: string;
  o: Row;
  lote?: Row;
  cabezas: string[];
  posiciones: Row[];
  venta: boolean;
  rev: number;
  onDone: () => void;
  onCambiar: () => void;
}) {
  const sim = useConsulta<Row>(path + "/simulador", rev);
  return (
    <Paso
      eyebrow="Revisar y aceptar"
      pregunta="¿Así quedó el trato?"
      explica="Compara la nota con lo que acordaron. El total lo calculó el servidor con las condiciones guardadas; todavía no cuenta como compra ni como deuda."
      tecnico={
        <>
          El total sale de <code>bovi.fn_calcular_liquidacion</code> (vía <code>GET …/simulador</code>) con <code>NUMERIC</code> y redondeo{" "}
          <code>HALF_UP</code> a 2 decimales: <code>base + cargos − descuentos</code>. El navegador nunca envía totales. Al aceptar, el comando{" "}
          <code>acordar_operacion</code> guarda las condiciones como una <code>contrato_version</code> inmutable y el trato pasa a{" "}
          <code>ACORDADA</code>.
        </>
      }
    >
      {sim.error && <Notice error={sim.error} />}
      <NotaTrato
        base={base}
        o={o}
        lote={lote}
        cabezas={cabezas}
        posiciones={posiciones}
        venta={venta}
        total={sim.data?.total}
        conceptos={sim.data?.conceptos as Row[] | undefined}
      />
      {Array.isArray(sim.data?.faltantes) && (sim.data!.faltantes as unknown[]).length > 0 && <p className="notice">Falta: {(sim.data!.faltantes as unknown[]).map(palabra).join(", ")}.</p>}
      <CommandForm path={path + "/acordar"} etag={etag} label="Aceptar las condiciones" build={() => ({})} onDone={onDone}>
        <p className="muted">Al aceptar, estas condiciones se guardan como versión fija. Si después cambian, se reabre y nace otra versión.</p>
      </CommandForm>
      <div className="paso-acciones">
        <button type="button" className="secondary" onClick={onCambiar}>
          Cambiar el precio
        </button>
      </div>
    </Paso>
  );
}

function PasoCerrar({
  base,
  path,
  etag,
  o,
  lote,
  cabezas,
  posiciones,
  venta,
  rev,
  onDone,
  onReabrir,
}: {
  base: string;
  path: string;
  etag?: string;
  o: Row;
  lote?: Row;
  cabezas: string[];
  posiciones: Row[];
  venta: boolean;
  rev: number;
  onDone: () => void;
  onReabrir: () => void;
}) {
  const sim = useConsulta<Row>(path + "/simulador", rev);
  return (
    <Paso
      eyebrow={venta ? "Cerrar la venta" : "Cerrar el trato"}
      pregunta={venta ? "¿Cerramos la venta?" : "¿Cerramos el trato?"}
      explica={
        venta
          ? "Cerrar es el único momento en que la venta cuenta: se crea lo que te deben y sale el costo de esas cabezas. Todo junto, o nada."
          : "Cerrar es el único momento en que la compra cuenta: entran las cabezas a tu inventario con su costo y se crea lo que debes. Todo junto, o nada."
      }
      tecnico={
        <>
          Comando <code>confirmar_operacion</code> en <strong>una sola transacción</strong>: reclama la <code>Idempotency-Key</code>, bloquea
          periodo → operación → posiciones (en orden de id) y crea posiciones de inventario, <code>liquidacion</code> con sus conceptos,
          asientos de valoración, auditoría y <code>evento_outbox</code>. Si algo falla, <code>ROLLBACK</code> total. Es el{" "}
          <strong>único evento económico</strong>: recibir, entregar o cobrar después no vuelven a crear venta ni deuda.
        </>
      }
    >
      <NotaTrato base={base} o={o} lote={lote} cabezas={cabezas} posiciones={posiciones} venta={venta} total={sim.data?.total} />
      <CommandForm
        path={path + "/confirmar"}
        etag={etag}
        label={venta ? "Cerrar la venta" : "Cerrar el trato"}
        build={(f) => ({ periodo_id: str(f, "periodo_id"), fecha_reconocimiento: str(f, "fecha_reconocimiento") })}
        onDone={onDone}
      >
        <Contable base={base} verbo="Se registra en" />
      </CommandForm>
      <details className="por-dentro">
        <summary>¿Hay que cambiar algo antes de cerrar?</summary>
        <CommandForm path={path + "/reabrir"} etag={etag} label="Reabrir las condiciones" build={() => ({})} onDone={onReabrir}>
          <p className="muted">La versión aceptada no se borra: se abre una propuesta nueva que tendrás que volver a aceptar.</p>
        </CommandForm>
      </details>
    </Paso>
  );
}

function PasoListo({
  base,
  o,
  venta,
  justo,
  ruta,
  go,
  lote,
  cabezas,
  posiciones,
  cobra,
}: {
  base: string;
  o: Row;
  venta: boolean;
  justo: boolean;
  ruta: string;
  go: Go;
  lote?: Row;
  cabezas: string[];
  posiciones: Row[];
  /** Solo caja y administración llevan al camino de cobro; al operador se le dice quién lo hace (sin botón muerto). */
  cobra: boolean;
}) {
  const liq = o.liquidacion as Row | undefined;
  if (o.estado !== "CONFIRMADA")
    return (
      <Paso eyebrow="Trato" pregunta={o.estado === "CANCELADA" ? "Este trato se canceló" : "Este trato se anuló"}>
        <p className="explica">No movió inventario ni dinero pendiente. Puedes empezar otro.</p>
        <div className="siguientes">
          <Siguiente titulo="Empezar otro trato" detalle="Desde el primer paso." onClick={() => go(ruta)} />
        </div>
      </Paso>
    );
  return (
    <Paso
      eyebrow={venta ? "Venta cerrada" : "Trato cerrado"}
      pregunta={venta ? "¡Venta cerrada!" : "¡Trato cerrado!"}
      explica={
        liq
          ? venta
            ? `${text(o.contraparte)} te debe ${money(liq.saldo)}.`
            : `Le debes ${money(liq.saldo)} a ${text(o.contraparte)}.`
          : "El trato quedó confirmado."
      }
      escena={<Fierro play={justo} label={venta ? "VENTA CERRADA" : "TRATO CERRADO"} />}
    >
      <p className="sr-only" role="status">
        {venta ? "Venta cerrada." : "Trato cerrado."} Folio {text(o.folio)}.
      </p>
      <div className="momento-final">
        <NotaTrato
          base={base}
          o={o}
          lote={lote}
          cabezas={cabezas}
          posiciones={posiciones}
          venta={venta}
          total={liq?.total}
        />
        <div className="siguientes">
          {venta ? (
            <Siguiente titulo="Entregar el ganado" detalle="Cuando las cabezas salgan con el comprador." onClick={() => go("camino-entregar", o)} />
          ) : (
            <Siguiente titulo="Recibir en el corral" detalle="Cuando las cabezas lleguen (si venían en camino)." onClick={() => go("camino-recibir", o)} />
          )}
          {liq &&
            (cobra ? (
              <Siguiente
                titulo={venta ? "Cobrarle" : "Pagarle"}
                detalle={venta ? "Apunta lo que te dé el comprador." : "Apunta lo que le entregues al vendedor."}
                onClick={() => go("camino-cobro", liq)}
              />
            ) : (
              <p className="siguiente-nota">Caja apunta el {venta ? "cobro" : "pago"} de este trato.</p>
            ))}
          {liq && <Siguiente titulo="Ver la liquidación" detalle="El desglose completo del cierre." onClick={() => go("liquidaciones", liq)} />}
          <Siguiente titulo={venta ? "Otra venta" : "Otro trato"} detalle="Empezar desde el primer paso." onClick={() => go(ruta)} />
        </div>
      </div>
    </Paso>
  );
}

// ───────────────────────── Recibir / entregar ─────────────────────────
export function CaminoMovimiento({
  base,
  sede,
  tipo,
  id,
  go,
}: {
  base: string;
  sede: Sede;
  tipo: "RECEPCION" | "ENTREGA";
  id?: string;
  go: Go;
}) {
  const entrega = tipo === "ENTREGA";
  const ruta = entrega ? "camino-entregar" : "camino-recibir";
  const escribe = sede.roles.some((r) => ESCRIBE.includes(r));
  const cobra = sede.roles.some((r) => COBRA.includes(r));
  const [rev, setRev] = useState(0);
  const [justo, setJusto] = useState(0);
  const op = useConsulta<Row>(id ? base + "/operaciones/" + id : undefined, rev);
  const pendientes = useConsulta<Page>(
    id
      ? base +
          "/inventario/posiciones?" +
          new URLSearchParams({ operacion_id: id, estado: entrega ? "VENDIDA_PENDIENTE_ENTREGA" : "PENDIENTE_RECEPCION", pagina: "1", tamano: "100" })
      : undefined,
    rev,
  );
  const lista = useConsulta<Page>(id ? undefined : base + "/operaciones?pagina=1&tamano=50&estado=CONFIRMADA&tipo=" + (entrega ? "VENTA" : "COMPRA"));
  const filas = pendientes.data?.elementos || [];
  const [sel, setSel] = useState<string[]>([]);
  useEffect(() => setSel(filas.map((f) => String(f.id))), [pendientes.data]);
  const actual = !id ? "cual" : justo ? "listo" : "cabezas";
  const pasos: [string, string][] = [
    ["cual", entrega ? "Qué venta" : "Qué compra"],
    ["cabezas", entrega ? "Qué salió" : "Qué llegó"],
    ["listo", "Listo"],
  ];
  if (!escribe)
    return (
      <section className="paso">
        <h2 className="pregunta">Este camino lo hace el operador</h2>
        <p className="explica">Tu rol puede consultar el inventario en Inventario → Posiciones.</p>
      </section>
    );
  const o = op.data;
  const liq = o?.liquidacion as Row | undefined;
  return (
    <div className="camino">
      <Rail
        titulo={entrega ? "Entregar ganado" : "Recibir en el corral"}
        subtitulo={o ? `${text(o.folio)} · ${text(o.contraparte)}` : entrega ? "Cabezas que salen" : "Cabezas que llegan"}
        pasos={pasos}
        actual={actual}
        alcanzado={actual}
        onPick={(p) => (p === "cual" ? go(ruta) : undefined)}
      />
      <div>
        {actual === "cual" && (
          <Paso
            eyebrow="Paso 1"
            pregunta={entrega ? "¿De qué venta sale el ganado?" : "¿De qué compra llega el ganado?"}
            explica={entrega ? "Solo aparecen ventas cerradas." : "Solo aparecen compras cerradas."}
            escena={entrega ? <CamionJaula /> : <PuertaCorral />}
          >
            {lista.error && <Notice error={lista.error} />}
            <div className="renglones">
              {[...(lista.data?.elementos || [])]
                .sort((a, b) => Number(a.estado_entrega === "COMPLETA") - Number(b.estado_entrega === "COMPLETA"))
                .map((r) => (
                  <button type="button" className="renglon" key={String(r.id)} onClick={() => go(ruta, r)}>
                    <span>
                      <strong className="mono">{text(r.folio)}</strong>
                      <small>
                        {text(r.contraparte)} · {fechaLarga(r.fecha_operacion)}
                      </small>
                    </span>
                    <span className="derecha">
                      <span className="badge" data-tone={r.estado_entrega === "PENDIENTE" ? "attention" : "positive"}>
                        {palabra(r.estado_entrega)}
                      </span>
                    </span>
                  </button>
                ))}
              {lista.loading && !lista.data && <p className="renglon">Buscando…</p>}
              {lista.data && !lista.data.elementos.length && (
                <p className="renglon">{entrega ? "No hay ventas cerradas todavía." : "No hay compras cerradas todavía."}</p>
              )}
            </div>
          </Paso>
        )}
        {actual === "cabezas" && (
          <Paso
            eyebrow="Paso 2"
            pregunta={entrega ? "¿Qué cabezas salieron?" : "¿Qué cabezas llegaron?"}
            explica={
              filas.length
                ? `${filas.length === 1 ? "Te marqué la única cabeza pendiente" : `Te marqué las ${filas.length} cabezas pendientes`}. Quita las que ${entrega ? "todavía no salen" : "todavía no llegan"}.`
                : undefined
            }
            escena={entrega ? <CamionJaula /> : <PuertaCorral />}
            tecnico={
              <>
                Comando <code>registrar_movimiento</code> tipo <code>{tipo}</code>:{" "}
                {entrega ? (
                  <>
                    las posiciones pasan de <code>VENDIDA_PENDIENTE_ENTREGA</code> a <code>CERRADA_VENTA</code>.
                  </>
                ) : (
                  <>
                    las posiciones pasan de <code>PENDIENTE_RECEPCION</code> a <code>DISPONIBLE</code>.
                  </>
                )}{" "}
                Es un hecho físico: <strong>no cambia el dinero</strong> ni crea otra venta o deuda (RN-020).
              </>
            }
          >
            {pendientes.error && <Notice error={pendientes.error} />}
            {pendientes.data && !filas.length ? (
              <>
                <p className="notice success">
                  {entrega ? "Ya no queda ganado pendiente de entrega en esta venta." : "Ya no queda ganado pendiente de recibir en esta compra."}
                </p>
                <div className="siguientes">
                  <Siguiente titulo={entrega ? "Otra venta" : "Otra compra"} detalle="Elegir otra operación." onClick={() => go(ruta)} />
                </div>
              </>
            ) : (
              <CommandForm
                key={rev}
                path={base + "/inventario/movimientos"}
                label={entrega ? "Ya salieron con el comprador" : "Ya llegaron al corral"}
                build={(f) => {
                  if (!sel.length) throw new Error("Marca al menos una cabeza.");
                  return {
                    tipo,
                    posiciones: sel,
                    ...(entrega ? { operacion_id: id } : {}),
                    ocurrido_en: new Date(str(f, "ocurrido_en")).toISOString(),
                  };
                }}
                onDone={() => {
                  setJusto((n) => n + 1);
                  setRev((n) => n + 1);
                }}
              >
                <div className="aretes" role="group" aria-label="Cabezas">
                  {filas.map((r) => {
                    const checked = sel.includes(String(r.id));
                    return (
                      <label className="arete-opcion" key={String(r.id)}>
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) =>
                            setSel((c) => (e.target.checked ? [...new Set([...c, String(r.id)])] : c.filter((x) => x !== String(r.id))))
                          }
                        />
                        <Arete code={arete(r)} selected={checked} />
                      </label>
                    );
                  })}
                </div>
                <p className="contador">
                  {sel.length} de {filas.length} marcadas
                </p>
                <div className="form-grid">
                  <Campo
                    name="ocurrido_en"
                    label={entrega ? "¿Cuándo salieron?" : "¿Cuándo llegaron?"}
                    type="datetime-local"
                    initial={localDentroDe(0)}
                  />
                </div>
              </CommandForm>
            )}
          </Paso>
        )}
        {actual === "listo" && (
          <Paso
            eyebrow="Listo"
            pregunta={entrega ? "¡Salió el ganado!" : "¡Ya están en el corral!"}
            explica={
              filas.length
                ? `Quedan ${filas.length} ${filas.length === 1 ? "cabeza" : "cabezas"} pendientes en este trato.`
                : entrega
                  ? "La venta quedó entregada completa. El dinero no cambió: eso se ve en la liquidación."
                  : "La compra quedó recibida completa. Las cabezas ya están disponibles para vender."
            }
            escena={entrega ? <CamionJaula play key={justo} /> : <PuertaCorral play key={justo} />}
          >
            <p className="sr-only" role="status">
              {entrega ? "Entrega registrada." : "Recepción registrada."}
            </p>
            <div className="siguientes">
              {filas.length > 0 && (
                <Siguiente titulo="Marcar las que faltan" detalle="Cuando lleguen o salgan." onClick={() => setJusto(0)} />
              )}
              {liq &&
                conSaldo(liq.saldo) &&
                (cobra ? (
                  <Siguiente
                    titulo={entrega ? "Cobrarle" : "Pagarle"}
                    detalle={`Saldo pendiente: ${money(liq.saldo)}.`}
                    onClick={() => go("camino-cobro", liq)}
                  />
                ) : (
                  <p className="siguiente-nota">
                    Caja apunta el {entrega ? "cobro" : "pago"} de este trato: quedan {money(liq.saldo)} pendientes.
                  </p>
                ))}
              <Siguiente titulo="Ver el inventario" detalle="Inventario → Posiciones." onClick={() => go("inventario")} />
            </div>
          </Paso>
        )}
      </div>
    </div>
  );
}

// ───────────────────────── Cobrar / pagar ─────────────────────────
export function CaminoCobro({ base, sede, id, go }: { base: string; sede: Sede; id?: string; go: Go }) {
  const caja = sede.roles.some((r) => COBRA.includes(r));
  const [rev, setRev] = useState(0);
  const [pago, setPago] = useState<Row>();
  const [justo, setJusto] = useState(false);
  const liq = useConsulta<Row>(id ? base + "/liquidaciones/" + id : undefined, rev);
  const partes = useConsulta<Page>(base + "/contrapartes?pagina=1&tamano=100");
  const ops = useConsulta<Page>(id ? undefined : base + "/operaciones?pagina=1&tamano=100&estado=CONFIRMADA");
  const lista = useConsulta<Page>(id ? undefined : base + "/liquidaciones?pagina=1&tamano=100", rev);
  const l = liq.data;
  const cobro = l?.direccion === "POR_COBRAR";
  const nombre = (parte: unknown) => text((partes.data?.elementos || []).find((p) => p.id === parte)?.nombre || "Contraparte");
  const previos = useConsulta<Page>(
    l && !pago ? base + "/pagos?" + new URLSearchParams({ pagina: "1", tamano: "50", tipo: cobro ? "COBRO" : "PAGO" }) : undefined,
    rev,
  );
  const aprovechables = (previos.data?.elementos || []).filter((p) => p.parte_id === l?.parte_id && conSaldo(p.disponible));
  const refrescarPago = (pid: string) =>
    request<Row>(base + "/pagos/" + pid)
      .then((r) => setPago(r.data))
      .catch(() => undefined);
  const actual = !id ? "cual" : justo ? "listo" : !pago ? "dinero" : pago.estado === "REGISTRADO" ? "revisar" : "abonar";
  const pasos: [string, string][] = [
    ["cual", "Qué cuenta"],
    ["dinero", "Cuánto"],
    ["revisar", "Revisar"],
    ["abonar", "Abonar"],
    ["listo", "Listo"],
  ];
  if (!caja)
    return (
      <section className="paso">
        <h2 className="pregunta">Este camino lo hace caja</h2>
        <p className="explica">Tu rol puede ver los saldos en Dinero → Cartera y en cada liquidación.</p>
      </section>
    );
  const saldo = importeDe(l?.saldo);
  const disponible = importeDe(pago?.disponible);
  const menor =
    disponible && saldo ? ((centavos(disponible) ?? 0n) < (centavos(saldo) ?? 0n) ? disponible : saldo) : saldo || disponible;
  const sugerido = importe(menor) ?? menor;
  return (
    <div className="camino">
      <Rail
        titulo="Cobrar o pagar"
        subtitulo={l ? `${cobro ? "Te debe" : "Le debes"}: ${nombre(l.parte_id)}` : "Dinero que entra o sale"}
        pasos={pasos}
        actual={actual}
        alcanzado={actual}
        onPick={(p) => (p === "cual" ? go("camino-cobro") : undefined)}
      />
      <div>
        {actual === "cual" && (
          <Paso
            eyebrow="Paso 1"
            pregunta="¿Qué cuenta vas a mover?"
            explica="Estas son las cuentas con saldo pendiente. «Te debe» es dinero que vas a cobrar; «Le debes» es dinero que vas a pagar."
            escena={<Libreta sello="COBRADO" />}
            tecnico={
              <>
                Cada cuenta es una <code>liquidacion</code> creada al cerrar un trato. Su saldo se calcula en SQL:{" "}
                <code>total + cargos − abonos − aplicaciones netas</code>.
              </>
            }
          >
            {lista.error && <Notice error={lista.error} />}
            <div className="renglones">
              {(lista.data?.elementos || [])
                .filter((x) => conSaldo(x.saldo))
                .map((x) => {
                  const folio = (ops.data?.elementos || []).find((o) => o.id === x.operacion_id)?.folio;
                  return (
                    <button type="button" className="renglon" key={String(x.id)} onClick={() => go("camino-cobro", x)}>
                      <span>
                        <strong>
                          {x.direccion === "POR_COBRAR" ? "Te debe" : "Le debes"} · {nombre(x.parte_id)}
                        </strong>
                        <small>
                          {folio ? text(folio) + " · " : ""}
                          {x.vence_el ? "vence " + fechaLarga(x.vence_el) : "sin vencimiento"}
                        </small>
                      </span>
                      <span className="derecha">{money(x.saldo)}</span>
                    </button>
                  );
                })}
              {lista.loading && !lista.data && <p className="renglon">Buscando…</p>}
              {lista.data && !lista.data.elementos.some((x) => conSaldo(x.saldo)) && (
                <p className="renglon">No hay cuentas con saldo pendiente. Todo está al corriente.</p>
              )}
            </div>
          </Paso>
        )}
        {actual === "dinero" && l && (
          <Paso
            eyebrow="Paso 2"
            pregunta={cobro ? "¿Cuánto te dieron?" : "¿Cuánto le das?"}
            explica={
              cobro
                ? `${nombre(l.parte_id)} te debe ${money(l.saldo)}. Apunta el dinero tal como llegó; si es un abono parcial, escribe solo esa parte.`
                : `Le debes a ${nombre(l.parte_id)} ${money(l.saldo)}. Apunta lo que le entregas, tal como sale de caja o del banco; si es un pago parcial, escribe solo esa parte.`
            }
            tecnico={
              <>
                Comando <code>registrar_pago</code>: el dinero queda <code>REGISTRADO</code> pero todavía <strong>no salda nada</strong>. Después
                se valida (alguien revisa que el dinero sí está) y se aplica a la cuenta. Son pasos separados a propósito: así se distingue el
                dinero recibido del dinero conciliado.
              </>
            }
          >
            {aprovechables.length > 0 && (
              <div className="pendientes-trato">
                <h3>Ya hay dinero apuntado de {nombre(l.parte_id)}</h3>
                <ul>
                  {aprovechables.map((p) => (
                    <li key={String(p.id)}>
                      <span>
                        {palabra(p.metodo)} · {fechaLarga(p.recibido_el)} · por aplicar <strong className="mono">{money(p.disponible)}</strong>{" "}
                        <span className="badge" data-tone={p.estado === "VALIDADO" ? "positive" : "progress"}>
                          {palabra(p.estado)}
                        </span>
                      </span>
                      <button type="button" className="secondary" onClick={() => setPago(p)}>
                        Usar este dinero
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <MetodoPago
              base={base}
              l={l}
              cobro={cobro}
              saldo={importe(saldo) ?? saldo}
              onDone={(p) => {
                setPago(p);
                void refrescarPago(String(p.id));
              }}
            />
          </Paso>
        )}
        {actual === "revisar" && l && pago && (
          <Paso
            eyebrow="Paso 3"
            pregunta={cobro ? "¿El dinero sí está completo?" : "¿El pago sí salió completo?"}
            explica={`Apuntaste ${money(pago.importe)} en ${palabra(pago.metodo).toLowerCase()}. Antes de abonarlo, ${revisionDe(cobro, pago.metodo)}.`}
            escena={<Libreta sello="REVISADO" />}
            tecnico={
              <>
                Comando <code>validar_pago</code>: pasa de <code>REGISTRADO</code> a <code>VALIDADO</code> y queda ligado al periodo contable.
                Solo caja o administración lo pueden hacer.
              </>
            }
          >
            <CommandForm
              path={base + "/pagos/" + pago.id + "/validar"}
              label={cobro ? "Sí, el dinero está completo" : "Sí, el pago salió completo"}
              build={(f) => ({ periodo_id: str(f, "periodo_id"), fecha_reconocimiento: str(f, "fecha_reconocimiento") })}
              onDone={() => void refrescarPago(String(pago.id))}
            >
              <Contable base={base} />
            </CommandForm>
          </Paso>
        )}
        {actual === "abonar" && l && pago && (
          <Paso
            eyebrow="Paso 4"
            pregunta="¿Cuánto abonas a esta cuenta?"
            explica={`Dinero por aplicar: ${money(pago.disponible)}. Saldo de la cuenta: ${money(l.saldo)}. Te propongo lo menor de los dos; lo que sobre queda ${cobro ? "a tu favor" : "como anticipo a " + nombre(l.parte_id)}.`}
            tecnico={
              <>
                Comando <code>aplicar_pago</code>: bloquea periodo → pagos → liquidaciones (en orden de id) y exige que lo aplicado no pase del
                disponible del pago ni del saldo de la cuenta (<code>BV020</code>). El sobrante no es una venta: es saldo a favor.
              </>
            }
          >
            <CommandForm
              path={base + "/pagos/" + pago.id + "/aplicaciones"}
              label="Abonar a la cuenta"
              build={(f) => ({
                periodo_id: str(f, "periodo_id"),
                fecha_reconocimiento: str(f, "fecha_reconocimiento"),
                aplicaciones: [{ liquidacion_id: l.id, importe: cash(str(f, "importe").trim()) }],
              })}
              onDone={() => {
                setJusto(true);
                setRev((n) => n + 1);
                void refrescarPago(String(pago.id));
              }}
            >
              <div className="form-grid">
                <Campo name="importe" label="Importe a abonar (MXN)" initial={sugerido} />
              </div>
              <Contable base={base} />
            </CommandForm>
          </Paso>
        )}
        {actual === "listo" && l && (
          <Paso
            eyebrow="Listo"
            pregunta={conSaldo(l.saldo) ? "¡Abono apuntado!" : "¡Cuenta saldada!"}
            explica={
              conSaldo(l.saldo)
                ? `Todavía ${cobro ? "te debe" : "le debes"} ${money(l.saldo)}.`
                : `${cobro ? nombre(l.parte_id) + " ya no te debe nada" : "Ya no le debes nada a " + nombre(l.parte_id)} en esta cuenta.`
            }
            escena={<Libreta play sello={conSaldo(l.saldo) ? "ABONADO" : "LIQUIDADO"} />}
          >
            <p className="sr-only" role="status">
              Abono registrado.
            </p>
            {pago && conSaldo(pago.disponible) && (
              <p className="notice">
                Sobraron {money(pago.disponible)}: quedan a favor de {nombre(l.parte_id)} como anticipo para otra cuenta.
              </p>
            )}
            <div className="siguientes">
              <Siguiente titulo="Otra cuenta" detalle="Cobrar o pagar otra." onClick={() => go("camino-cobro")} />
              <Siguiente titulo="Ver la liquidación" detalle="Desglose y movimientos." onClick={() => go("liquidaciones", l)} />
            </div>
          </Paso>
        )}
        {id && liq.error && <Notice error={liq.error} />}
      </div>
    </div>
  );
}

/** Qué revisar antes de abonar, según si el dinero entra (cobro) o sale (pago) y cómo se movió. */
function revisionDe(cobro: boolean, metodo: unknown) {
  if (cobro)
    return metodo === "TRANSFERENCIA"
      ? "confirma que el depósito ya aparece en tu banco"
      : metodo === "CHEQUE"
        ? "confirma que el cheque está a tu nombre y firmado"
        : metodo === "EFECTIVO"
          ? "confirma que los billetes están contados"
          : "confirma que el dinero sí llegó completo";
  return metodo === "TRANSFERENCIA"
    ? "confirma que la transferencia ya salió de tu cuenta"
    : metodo === "CHEQUE"
      ? "confirma que entregaste el cheque firmado"
      : metodo === "EFECTIVO"
        ? "confirma que entregaste los billetes contados"
        : "confirma que el pago sí se entregó completo";
}

function MetodoPago({ base, l, cobro, saldo, onDone }: { base: string; l: Row; cobro: boolean; saldo: string; onDone: (p: Row) => void }) {
  const [metodo, setMetodo] = useState("EFECTIVO");
  return (
    <CommandForm
      path={base + "/pagos"}
      label={cobro ? "Apuntar el cobro" : "Apuntar el pago"}
      build={(f) => ({
        parte_id: l.parte_id,
        tipo: cobro ? "COBRO" : "PAGO",
        importe: cash(str(f, "importe").trim()),
        metodo,
        referencia: str(f, "referencia"),
        recibido_el: str(f, "recibido_el"),
      })}
      onDone={onDone}
    >
      <Opciones
        name="metodo"
        legend="¿Cómo?"
        value={metodo}
        onChange={setMetodo}
        options={[
          { value: "EFECTIVO", titulo: "Efectivo", hint: cobro ? "Billetes contados en mano." : "Billetes contados que entregas.", escena: <MiniPago metodo="EFECTIVO" /> },
          { value: "TRANSFERENCIA", titulo: "Transferencia", hint: cobro ? "SPEI o depósito a tu banco." : "SPEI desde tu banco.", escena: <MiniPago metodo="TRANSFERENCIA" /> },
          { value: "CHEQUE", titulo: "Cheque", hint: "Anota el número en la referencia.", escena: <MiniPago metodo="CHEQUE" /> },
          { value: "OTRO", titulo: "Otro", hint: "Explícalo en la referencia.", escena: <MiniPago metodo="OTRO" /> },
        ]}
      />
      <div className="form-grid">
        <Campo name="importe" label="Importe (MXN)" initial={saldo} help="Por ejemplo 1,250.50. Si es un abono, escribe solo esa parte." />
        <Campo name="recibido_el" label={cobro ? "¿Qué día te lo dieron?" : "¿Qué día se lo diste?"} type="date" initial={today()} />
        <Campo name="referencia" label="Referencia" required={false} help="Folio de la transferencia, número de cheque o una nota." />
      </div>
    </CommandForm>
  );
}
