export const MAX_ASSETS = 12

export const DEFAULT_SETTINGS = { horizon: 10, simulations: 10000, days: 730 }

export const LIMITS = {
  horizon: { min: 1, max: 90, label: 'Horizon (days)' },
  simulations: { min: 1000, max: 100000, label: 'Simulations' },
  days: { min: 150, max: 4000, label: 'History (days)' },
}

// in development the Vite dev server forwards /api to Cloud Run (see vite.config.js). for a deployed site set VITE_API_URL.
export const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : '')

export const HORIZON_CHOICES = [10, 30, 90]
