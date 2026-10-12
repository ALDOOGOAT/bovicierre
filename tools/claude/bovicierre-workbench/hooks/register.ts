import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Campaign } from '../types'
import {
  CHECKPOINT_MS, MARKER, areasFor, campaignActive, checkpointDue, parseStatus,
  quotaLevel, quotaText, relativeTo, satisfied,
} from './logic'

const campaign = atom({ plugin: 'bovicierre-workbench', key: 'campaign' } as const, { active: false, root: '', reason: 'sin evaluar' } as Campaign)
const stale = atom({ plugin: 'bovicierre-workbench', key: 'stale' } as const, [] as string[])
const lastCheckpointAt = atom({ plugin: 'bovicierre-workbench', key: 'lastCheckpointAt' } as const, 0)
const warned = atom({ plugin: 'bovicierre-workbench', key: 'warned' } as const, 0)

const text = async ($: any, path: string) => ((await $.fs.exists(path)) ? String(await $.fs.read(path)) : null)

export const register: Register = on => {
  // Mod 1: control de sesión y continuidad.
  on('session.start', async ($, e, next) => {
    const root = e.cwd
    const status = parseStatus(await text($, `${root}/docs/continuity/SESSION_STATE.md`))
    const verdict = campaignActive({
      gitConfig: await text($, `${root}/.git/config`),
      marker: await $.fs.exists(`${root}/${MARKER}`),
      stop: await $.fs.exists(`${root}/docs/continuity/STOP`),
      status,
    })
    await update($, campaign, () => ({ ...verdict, root }))
    if (!verdict.active) return next(e)
    await update($, lastCheckpointAt, () => $.clock.now())
    await $.command.register({ name: 'bovi-status', description: 'Estado de la campaña BoviCierre: bloque, cuota y comprobaciones pendientes' })
    $.ui.status(`Bovi ${status ?? 'sin checkpoint'} · leer docs/continuity/NEXT_SESSION.md`)
    $.clock.every(5 * 60 * 1000, async () => {
      const u = await $.session.usage()
      const level = quotaLevel(u.rateLimits)
      const pending = await read($, stale)
      $.ui.status(`Bovi ${status ?? '?'} · ${quotaText(u.rateLimits)} · ${pending.length} verif. pendientes`)
      if (level > (await read($, warned))) {
        await update($, warned, () => level)
        $.ui.toast(level === 90 ? 'Cuota ≥90 %: consolidar y entregar checkpoint corto.' : 'Cuota ≥80 %: reducir trabajo nuevo y guardar checkpoint.')
      }
      if (checkpointDue($.clock.now(), await read($, lastCheckpointAt))) {
        await update($, lastCheckpointAt, () => $.clock.now())
        $.ui.toast('Checkpoint debido: python3 tools/claude/checkpoint.py save …')
      }
    })
    return next(e)
  })

  on('command.run', { command: 'bovi-status' }, async $ => {
    const c = await read($, campaign)
    const u = await $.session.usage()
    const pending = await read($, stale)
    return { text: `Campaña: ${c.reason}. ${quotaText(u.rateLimits)}. Verificaciones pendientes: ${pending.join(', ') || 'ninguna'}. Intervalo de checkpoint ${CHECKPOINT_MS / 60000} min.` }
  })

  // Mod 2: control de evidencia (marca stale lo afectado; sólo un comando exitoso lo limpia).
  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    const c = await read($, campaign)
    if (!c.active || ran.deny !== undefined || ran.isError) return ran
    const input = e as any
    if (e.tool === 'Edit' || e.tool === 'Write') {
      const rel = relativeTo(c.root, String(input.file_path ?? ''))
      const areas = rel ? areasFor(rel) : []
      if (areas.length) await update($, stale, s => [...new Set([...s, ...areas])])
    } else if (e.tool === 'Bash') {
      const ok = satisfied(String(input.command ?? ''))
      if (ok.length) await update($, stale, s => s.filter(a => !ok.includes(a)))
    }
    return ran
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))
}
