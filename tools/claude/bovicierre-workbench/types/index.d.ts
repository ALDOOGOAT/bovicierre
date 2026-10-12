export type Campaign = { active: boolean; root: string; reason: string }

declare module 'claude-code' {
  interface PluginState {
    'bovicierre-workbench': {
      campaign: Campaign
      stale: string[]
      lastCheckpointAt: number
      warned: number
    }
  }
}
