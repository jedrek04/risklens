const toRgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))

export function mix(from, to, t) {
  const a = toRgb(from)
  const b = toRgb(to)
  return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * t).toString(16).padStart(2, '0')).join('')
}

const NEUTRAL = '#383835'
const POSITIVE = '#3987e5'
const NEGATIVE = '#e66767'

// grey in the middle, blue for assets that move together, red for assets that move apart
export const correlationColor = (v) => (v >= 0 ? mix(NEUTRAL, POSITIVE, Math.min(1, v)) : mix(NEUTRAL, NEGATIVE, Math.min(1, -v)))

// quiet cell for a normal day, a brighter blue the more unusual the day was
export const QUIET_DAY = '#1c2436'
export const unusualColor = (score) => mix('#173a6b', '#9ec5f4', 0.2 + 0.8 * Math.min(1, Math.max(0, score) / 0.14))
