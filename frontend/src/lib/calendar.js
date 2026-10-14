export const LABEL_WIDTH = 92
export const WIDTH = 1000
export const ROW_HEIGHT = 22
export const ROW_GAP = 6
const TOP = 24
const DAY = 86400000

const toMs = (date) => Date.parse(`${date}T00:00:00Z`)

// places every day of every row on one shared time axis. rows need { dates, scores, anomaly }.
export function calendarLayout(rows) {
  const times = rows.flatMap((row) => row.dates.map(toMs))
  const start = Math.min(...times)
  const end = Math.max(...times)
  const length = end - start || 1
  const x = (t) => LABEL_WIDTH + ((t - start) / length) * (WIDTH - LABEL_WIDTH)
  const slot = (WIDTH - LABEL_WIDTH) / (length / DAY)

  const placed = rows.map((row, i) => ({
    ...row,
    y: TOP + i * (ROW_HEIGHT + ROW_GAP),
    cells: row.dates.map((date, k) => ({ date, x: x(toMs(date)), score: row.scores[k], flag: row.anomaly[k] })),
  }))

  const months = []
  const first = new Date(start)
  const nextMonth = (d) => new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1))
  for (let d = nextMonth(first); +d <= end; d = nextMonth(d)) {
    const month = d.toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' })
    months.push({ x: x(+d), label: d.getUTCMonth() === 0 ? `${month} '${String(d.getUTCFullYear()).slice(2)}` : month })
  }

  return {
    rows: placed,
    months,
    cellWidth: Math.max(1.8, slot * 0.8),
    height: TOP + rows.length * (ROW_HEIGHT + ROW_GAP) + 6,
  }
}

export const rowAt = (layout, y) => layout.rows.findIndex((row) => y >= row.y - ROW_GAP / 2 && y <= row.y + ROW_HEIGHT + ROW_GAP / 2)

export function nearestCell(row, x, maxDistance = 10) {
  let best = null
  let bestDistance = Infinity
  for (const cell of row.cells) {
    const distance = Math.abs(cell.x - x)
    if (distance < bestDistance) {
      best = cell
      bestDistance = distance
    }
  }
  return bestDistance <= maxDistance ? best : null
}
