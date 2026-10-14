// -1 is the left end of the gauge, 0 the top, +1 the right end
export const gaugeAngle = (score) => Math.PI * (1 - (score + 1) / 2)

export const confidenceRatio = (headlines, needed) => Math.min(1, headlines / needed)

export function statusInfo(status) {
  if (status === 'ok') return { text: '✓ Reliable', good: true }
  if (status === 'low_confidence') return { text: '⚠ Low confidence', good: false }
  return { text: '— No news', good: false }
}

// headline links come from the internet, only plain web links may be opened
export function safeUrl(url) {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? parsed.href : null
  } catch {
    return null
  }
}
