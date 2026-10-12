// Carga HTTP mixta autenticada contra la instancia LOCAL de BoviCierre (k6 v1.0.0).
// 70 % lecturas operativas, 20 % borradores válidos, 10 % comandos sobre recursos propios del VU.
// Cada VU tiene su propia sesión (cookie + CSRF). Las carreras sobre un mismo recurso NO están aquí (ver db/tests).
// Uso: BOVI_RUN=<id> k6 run --summary-export <dir>/summary.json tests/performance/load.js
import http from 'k6/http';
import {check, fail, group, sleep} from 'k6';
import {Counter, Trend} from 'k6/metrics';
import exec from 'k6/execution';

const BASE = __ENV.BOVI_API_TEST_URL || 'http://127.0.0.1:15180/api/v1';
if (!/^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?\//.test(BASE)) fail('Sólo se permite la instancia local');
const RUN = __ENV.BOVI_RUN || String(Date.now());
const SECRETS = (__ENV.BOVI_SECRET_DIR || '') + '/';
const USERS = [
  {login: 'demo.admin', secret: open(SECRETS + 'demo_password').trim(), writer: true},
  {login: 'demo.operador', secret: open(SECRETS + 'demo_operador_password').trim(), writer: true},
  {login: 'demo.caja', secret: open(SECRETS + 'demo_caja_password').trim(), writer: false},
  {login: 'demo.auditor', secret: open(SECRETS + 'demo_auditor_password').trim(), writer: false},
];
const PROFILE = __ENV.BOVI_PROFILE || 'ramp';
const stages = PROFILE === 'smoke'
  ? [{duration: '20s', target: 2}]
  : [{duration: '1m', target: 1}, {duration: '1m', target: 5}, {duration: '2m', target: 10}, {duration: '3m', target: 20}, {duration: '30s', target: 0}];

export const options = {
  scenarios: {mixto: {executor: 'ramping-vus', startVUs: 1, stages, gracefulRampDown: '20s'}},
  thresholds: {
    'http_req_failed{esperado:si}': ['rate<0.01'],
    'lectura_ms': ['p(95)<500'],
    'escritura_ms': ['p(95)<1000'],
    'checks': ['rate>0.99'],
  },
  summaryTrendStats: ['min', 'med', 'avg', 'p(90)', 'p(95)', 'p(99)', 'max'],
  noCookiesReset: true,
};

const lectura = new Trend('lectura_ms', true);
const escritura = new Trend('escritura_ms', true);
const creados = new Counter('efectos_creados');
const fallosNoEsperados = new Counter('fallos_no_esperados');
let session = null;

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}
function csrf() {
  const r = http.get(`${BASE}/sesion/csrf`, {tags: {name: 'csrf', esperado: 'si'}});
  return {[r.json('headerName')]: r.json('token')};
}
function login() {
  const user = USERS[(exec.vu.idInTest - 1) % USERS.length];
  let token = csrf();
  const r = http.post(`${BASE}/sesion/login`, JSON.stringify({login: user.login, contrasena: user.secret}),
    {headers: {'Content-Type': 'application/json', ...token}, tags: {name: 'login', esperado: 'si'}});
  if (!check(r, {'login 204': x => x.status === 204})) { fallosNoEsperados.add(1); fail(`login ${user.login} HTTP ${r.status}`); }
  token = csrf();
  const me = http.get(`${BASE}/sesion/actual`, {tags: {name: 'sesion_actual', esperado: 'si'}});
  const site = me.json('sedes').find(s => s.codigo === 'DEMO-A').id;
  const parties = http.get(`${BASE}/sedes/${site}/contrapartes?pagina=1&tamano=20`, {tags: {name: 'contrapartes', esperado: 'si'}});
  return {user, site, token, party: parties.json('elementos.0.id'), ops: []};
}
function read(name, path) {
  const r = http.get(`${BASE}${path}`, {tags: {name, esperado: 'si'}});
  lectura.add(r.timings.duration, {familia: name});
  if (!check(r, {[`${name} 200`]: x => x.status === 200})) fallosNoEsperados.add(1, {familia: name});
  return r;
}
function write(name, path, body, expect = [201, 200]) {
  const r = http.post(`${BASE}${path}`, JSON.stringify(body), {
    headers: {'Content-Type': 'application/json', 'Idempotency-Key': uuid(), ...session.token},
    tags: {name, esperado: 'si'}});
  escritura.add(r.timings.duration, {familia: name});
  if (check(r, {[`${name} ${expect.join('/')}`]: x => expect.includes(x.status)})) creados.add(1, {familia: name});
  else fallosNoEsperados.add(1, {familia: name});
  return r;
}

export default function () {
  if (!session) session = login();
  const s = `/sedes/${session.site}`;
  const roll = Math.random();
  if (roll < 0.70 || !session.user.writer) {
    group('lecturas', () => {
      const pick = Math.floor(Math.random() * 6);
      if (pick === 0) read('operaciones', `${s}/operaciones?pagina=1&tamano=20`);
      else if (pick === 1) read('inventario', `${s}/inventario/posiciones?pagina=1&tamano=20`);
      else if (pick === 2) read('cartera', `${s}/reportes/cartera`);
      else if (pick === 3) read('liquidaciones', `${s}/liquidaciones?pagina=1&tamano=20`);
      else if (pick === 4) read('margen', `${s}/reportes/margen`);
      else {
        const list = read('operaciones_busqueda', `${s}/operaciones?pagina=1&tamano=5&q=C-2026`);
        const id = list.json('elementos.0.id');
        if (id) read('expediente', `${s}/operaciones/${id}/expediente`);
      }
    });
  } else if (roll < 0.90) {
    group('borradores', () => {
      const r = write('borrador_compra', `${s}/operaciones`, {tipo: 'COMPRA', parte_id: session.party, fecha_operacion: '2026-10-12', requiere_recepcion: false});
      if (r.status === 201) session.ops.push(r.json('id'));
    });
  } else {
    group('comandos', () => {
      const tag = `${RUN}V${exec.vu.idInTest}I${exec.vu.iterationInScenario}`;  // letras como separador: fn_codigo elimina guiones y "13-61" chocaba con "136-1"
      if (Math.random() < 0.5) write('alta_contraparte', `${s}/contrapartes`, {nombre: `DEMO CARGA ${tag}`, tipo_persona: 'FISICA'});
      else write('alta_animal', `${s}/animales`, {sexo: 'M', identificaciones: [{sistema: 'INTERNO', codigo: `DEMO-CARGA-${tag}`}]});
    });
  }
  sleep(0.3 + Math.random() * 0.5);  // tiempo de reflexión: sesiones, no un bucle cerrado
}
