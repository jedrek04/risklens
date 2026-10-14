export function sparkline(values, width, height, pad = 4) {
  const low = Math.min(...values)
  const high = Math.max(...values)
  const span = high - low || 1e-9
  const x = (i) => pad + (i / Math.max(1, values.length - 1)) * (width - pad * 2 - 6)
  const y = (v) => pad + (1 - (v - low) / span) * (height - pad * 2 - 2)
  return {
    path: values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(''),
    end: { x: x(values.length - 1), y: y(values[values.length - 1]) },
  }
}
