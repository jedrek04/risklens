// the same rule the backend uses to check the report: every number in the text must exist in the fact sheet
const NUMBER = /\d+(?:\.\d+)?/g

const LABELS = {
  var: 'Value at Risk',
  cvar: 'Expected shortfall',
  portfolio_volatility: 'Portfolio volatility',
  horizon_days: 'Horizon (days)',
  confidence: 'Confidence',
  history_days: 'History (days)',
  simulations: 'Simulations',
  annualized_volatility: 'Annualised volatility',
  current_daily_volatility: 'Daily volatility today',
  weight: 'Weight',
  correlation: 'Correlation',
  flagged_days: 'Unusual days',
  scored_days: 'Days scored',
  score: 'Sentiment score',
  headlines: 'Headlines',
}

export function flattenFacts(value, path = []) {
  if (value !== null && typeof value === 'object') {
    return Object.entries(value).flatMap(([key, child]) => flattenFacts(child, [...path, key]))
  }
  return [{ path, value: String(value) }]
}

// number value -> position of the first fact that contains it. compared by value like the backend does, so 9 matches 09 and 5 matches 5.0
export function factIndex(facts) {
  const index = new Map()
  facts.forEach((fact, i) => {
    for (const number of fact.value.match(NUMBER) ?? []) {
      if (!index.has(Number(number))) index.set(Number(number), i)
    }
  })
  return index
}

// cuts a text into pieces, and says for each number which fact it matches (or null if none)
export function annotate(text, index) {
  const parts = []
  let last = 0
  for (const match of text.matchAll(NUMBER)) {
    if (match.index > last) parts.push({ text: text.slice(last, match.index), fact: null })
    parts.push({ text: match[0], fact: index.get(Number(match[0])) ?? null, isNumber: true })
    last = match.index + match[0].length
  }
  if (last < text.length) parts.push({ text: text.slice(last), fact: null })
  return parts
}

export function verifiedCount(texts, index) {
  let numbers = 0
  let verified = 0
  for (const text of texts) {
    for (const part of annotate(text, index)) {
      if (!part.isNumber) continue
      numbers += 1
      if (part.fact !== null) verified += 1
    }
  }
  return { numbers, verified }
}

export function factLabel(path) {
  return path
    .filter((p) => !/^\d+$/.test(p))
    .slice(-2)
    .map((p) => LABELS[p] ?? p.replace(/_/g, ' '))
    .join(' · ')
}

export const reportTexts = (report) => [
  report.title,
  ...report.sections.flatMap((s) => [s.body, ...(s.bullets ?? [])]),
]
