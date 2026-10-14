import { LIMITS } from '../config'

export function validateSettings(settings) {
  const errors = {}
  for (const [key, { min, max }] of Object.entries(LIMITS)) {
    const value = settings[key]
    if (!Number.isInteger(value) || value < min || value > max) {
      errors[key] = `${min.toLocaleString('en-US')} to ${max.toLocaleString('en-US')}`
    }
  }
  return errors
}
