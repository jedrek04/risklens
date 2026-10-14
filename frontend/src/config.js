export const MAX_ASSETS = 12

export const DEFAULT_SETTINGS = { horizon: 10, simulations: 10000, days: 730 }

export const LIMITS = {
  horizon: { min: 1, max: 90, label: 'Horizon (days)' },
  simulations: { min: 1000, max: 100000, label: 'Simulations' },
  days: { min: 150, max: 4000, label: 'History (days)' },
}
