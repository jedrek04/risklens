const MINUS = '−'

export function percent(value, digits = 1, { sign = false } = {}) {
  const x = value * 100
  const text = Math.abs(x).toFixed(digits)
  if (x < 0 && Number(text) !== 0) return `${MINUS}${text}%`
  return `${sign && Number(text) !== 0 ? '+' : ''}${text}%`
}

export function signed(value, digits = 2) {
  const text = Math.abs(value).toFixed(digits)
  if (Number(text) === 0) return text
  return `${value < 0 ? MINUS : '+'}${text}`
}

export const seconds = (value) => `${value.toFixed(1)} s`
