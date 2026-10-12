// Lógica pura y determinista de los dos mods; sin acceso al engine para poder probarla.

export const REMOTE = 'ALDOOGOAT/bovicierre'
export const MARKER = 'docs/continuity/campaign.marker'
export const TERMINAL = ['DONE', 'BLOCKED_PERMISSION', 'USER_STOPPED']
export const CHECKPOINT_MS = 25 * 60 * 1000

/** Activa sólo con remote BoviCierre + marcador + sin STOP + estado no terminal. */
export function campaignActive(i: { gitConfig: string | null; marker: boolean; stop: boolean; status: string | null }) {
  if (!i.gitConfig || !i.gitConfig.includes(REMOTE)) return { active: false, reason: 'repositorio no BoviCierre' }
  if (!i.marker) return { active: false, reason: 'sin marcador de campaña' }
  if (i.stop) return { active: false, reason: 'STOP' }
  if (i.status && TERMINAL.includes(i.status)) return { active: false, reason: `estado ${i.status}` }
  return { active: true, reason: 'campaña autorizada' }
}

/** Extrae el estado del resumen versionado SESSION_STATE.md. */
export function parseStatus(md: string | null): string | null {
  const m = md?.match(/\| Estado \| \*\*([A-Z0-9_]+)\*\* \|/)
  return m ? m[1] : null
}

export type Limit = { kind: string; percentUsed: number; resetsAt?: string }

/** Texto de cuota: nunca inventa 0 % ni reset cuando no hay lectura. */
export function quotaText(limits: Limit[]): string {
  const five = limits.find(l => l.kind === 'five_hour')
  if (!five) return 'cuota desconocida'
  return `5h ${Math.round(five.percentUsed)}%` + (five.resetsAt ? ` reset ${five.resetsAt.slice(11, 16)}Z` : '')
}

/** Política de campaña: 0 normal, 80 reducir trabajo nuevo, 90 consolidar. */
export function quotaLevel(limits: Limit[]): 0 | 80 | 90 {
  const five = limits.find(l => l.kind === 'five_hour')
  if (!five) return 0
  return five.percentUsed >= 90 ? 90 : five.percentUsed >= 80 ? 80 : 0
}

/** Checkpoint debido si pasó el intervalo; un salto de reloj hacia atrás no duplica avisos. */
export function checkpointDue(now: number, last: number) {
  return now >= last && now - last >= CHECKPOINT_MS
}

// Matriz área modificada → comprobación afectada.
const AREAS: [RegExp, string][] = [
  [/^frontend\/src\/.*\.css$/, 'ui-visual'],
  [/^frontend\/src\//, 'frontend-unit-e2e'],
  [/^backend\/src\/main\/.*\/acceso\//, 'auth-csrf-sesion'],
  [/^backend\/src\//, 'backend-http'],
  [/^db\/migrations\//, 'sql-gold'],
  [/^docs\/api\/openapi\.yaml$/, 'contrato-api'],
  [/^docs\/database\//, 'mer-relacional'],
]

export function areasFor(relPath: string): string[] {
  const hit = AREAS.filter(([re]) => re.test(relPath)).map(([, a]) => a)
  return [...new Set(hit)]
}

// Comando de verificación → áreas que satisface (sólo si terminó sin error).
// Sólo cuenta si el comando EMPIEZA por la verificación (tras variables de entorno opcionales):
// `echo verify-sql` o `grep test:e2e` no satisfacen nada (hallazgo SF-17).
const ENV = String.raw`^\s*(?:[A-Z_][A-Z0-9_]*=\S+\s+)*`
const CHECKS: [RegExp, string[]][] = [
  [new RegExp(ENV + String.raw`(?:npm --prefix frontend run test:e2e|npx playwright test)\b`), ['frontend-unit-e2e', 'ui-visual']],
  [new RegExp(ENV + String.raw`npm (?:--prefix frontend )?(?:run )?(?:test|build|typecheck)\b`), ['frontend-unit-e2e']],
  [new RegExp(ENV + String.raw`(?:\./backend/mvnw\b.*\bverify\b|make verify-api\b)`), ['backend-http', 'auth-csrf-sesion']],
  [new RegExp(ENV + String.raw`make verify-sql\b`), ['sql-gold']],
  [new RegExp(ENV + String.raw`(?:make verify-docs\b|npx -y @redocly/cli@\S+ lint\b)`), ['contrato-api', 'mer-relacional']],
]

export function satisfied(command: string): string[] {
  return CHECKS.filter(([re]) => re.test(command)).flatMap(([, a]) => a)
}

export function relativeTo(root: string, file: string): string | null {
  const r = root.endsWith('/') ? root : root + '/'
  if (!file.startsWith(r) || file.includes('/../')) return null
  return file.slice(r.length)
}
