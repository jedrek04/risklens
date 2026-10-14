// round tick values for an axis, for example 0, 0.025, 0.05
export function niceTicks(low, high, count = 5) {
  const raw = (high - low) / count
  const magnitude = Math.pow(10, Math.floor(Math.log10(raw)))
  const f = raw / magnitude
  const step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * magnitude

  const ticks = []
  for (let v = Math.ceil(low / step) * step; v <= high + 1e-9; v += step) {
    ticks.push(Math.abs(v) < 1e-12 ? 0 : v)
  }
  return ticks
}

// how many decimals a percent axis needs so labels do not round into each other (2.5% must not show as 3%)
export function tickDecimals(ticks) {
  if (ticks.length < 2) return 0
  const stepPercent = (ticks[1] - ticks[0]) * 100
  return Number.isInteger(Number(stepPercent.toFixed(6))) ? 0 : 1
}
