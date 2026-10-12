import { expect, test } from 'claude-code/testing'

import {
  areasFor, campaignActive, checkpointDue, CHECKPOINT_MS, parseStatus, quotaLevel, quotaText, relativeTo, satisfied,
} from './logic'

const cfg = '[remote "origin"]\n url = https://github.com/ALDOOGOAT/bovicierre.git'

test('otro repo no activa la campaña', () => {
  expect(campaignActive({ gitConfig: 'url = https://github.com/x/y', marker: true, stop: false, status: null }).active).toBe(false)
  expect(campaignActive({ gitConfig: null, marker: true, stop: false, status: null }).active).toBe(false)
})

test('STOP y estados terminales no reanudan', () => {
  expect(campaignActive({ gitConfig: cfg, marker: true, stop: true, status: 'S1_RUNNING' }).active).toBe(false)
  for (const s of ['DONE', 'USER_STOPPED', 'BLOCKED_PERMISSION'])
    expect(campaignActive({ gitConfig: cfg, marker: true, stop: false, status: s }).active).toBe(false)
  expect(campaignActive({ gitConfig: cfg, marker: false, stop: false, status: 'S1_RUNNING' }).active).toBe(false)
  expect(campaignActive({ gitConfig: cfg, marker: true, stop: false, status: 'S1_RUNNING' }).active).toBe(true)
})

test('cuota desconocida no inventa porcentaje ni reset', () => {
  expect(quotaText([])).toBe('cuota desconocida')
  expect(quotaLevel([])).toBe(0)
  expect(quotaText([{ kind: 'five_hour', percentUsed: 81.4 }])).toBe('5h 81%')
  expect(quotaLevel([{ kind: 'five_hour', percentUsed: 92 }])).toBe(90)
})

test('salto de reloj hacia atrás no dispara checkpoint duplicado', () => {
  expect(checkpointDue(1000, 5000)).toBe(false)
  expect(checkpointDue(CHECKPOINT_MS + 1, 0)).toBe(true)
  expect(checkpointDue(CHECKPOINT_MS - 1, 0)).toBe(false)
})

test('cambio nuevo vuelve obsoleta la evidencia y sólo la verificación correcta la limpia', () => {
  expect(areasFor('frontend/src/styles.css')).toEqual(['ui-visual', 'frontend-unit-e2e'])
  expect(areasFor('db/migrations/V14__x.sql')).toEqual(['sql-gold'])
  expect(areasFor('README.md')).toEqual([])
  expect(satisfied('BOVI_UI_TEST_URL=http://127.0.0.1:15180 npm --prefix frontend run test:e2e -- closure.spec.ts')).toContain('ui-visual')
  expect(satisfied('git status')).toEqual([])
  expect(satisfied('echo verify-sql')).toEqual([])
  expect(satisfied('grep -r test:e2e .')).toEqual([])
  expect(satisfied('BOVI_API_IT=true ./backend/mvnw -q -f backend/pom.xml verify')).toContain('backend-http')
  expect(satisfied('make verify-sql')).toEqual(['sql-gold'])
})

test('estado y rutas', () => {
  expect(parseStatus('| Estado | **S1_RUNNING** |')).toBe('S1_RUNNING')
  expect(parseStatus(null)).toBe(null)
  expect(relativeTo('/r', '/r/frontend/src/a.ts')).toBe('frontend/src/a.ts')
  expect(relativeTo('/r', '/r/../etc/passwd')).toBe(null)
  expect(relativeTo('/r', '/otro/a.ts')).toBe(null)
})
