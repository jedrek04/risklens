import { describe, expect, it } from 'vitest'
import { calendarLayout, nearestCell, rowAt } from './calendar'
import { correlationColor, mix, unusualColor } from './color'
import { confidenceRatio, gaugeAngle, safeUrl, statusInfo } from './sentiment'
import { sparkline } from './sparkline'

describe('colours', () => {
  it('mix returns the ends and the middle', () => {
    expect(mix('#000000', '#ffffff', 0)).toBe('#000000')
    expect(mix('#000000', '#ffffff', 1)).toBe('#ffffff')
    expect(mix('#000000', '#ffffff', 0.5)).toBe('#808080')
  })

  it('correlation is grey at 0, blue at +1 and red at minus 1', () => {
    expect(correlationColor(0)).toBe('#383835')
    expect(correlationColor(1)).toBe('#3987e5')
    expect(correlationColor(-1)).toBe('#e66767')
    expect(correlationColor(5)).toBe('#3987e5')
  })

  it('a more unusual day is brighter', () => {
    const brightness = (hex) => [1, 3, 5].reduce((s, i) => s + parseInt(hex.slice(i, i + 2), 16), 0)
    expect(brightness(unusualColor(0.14))).toBeGreaterThan(brightness(unusualColor(0.05)))
    expect(brightness(unusualColor(0.05))).toBeGreaterThan(brightness(unusualColor(0.001)))
  })
})

describe('unusual days calendar', () => {
  const row = (dates, flagged = []) => ({
    dates,
    scores: dates.map((d) => (flagged.includes(d) ? 0.1 : -0.1)),
    anomaly: dates.map((d) => flagged.includes(d)),
  })
  const layout = calendarLayout([
    row(['2026-01-05', '2026-02-10', '2026-03-20'], ['2026-02-10']),
    row(['2026-01-06', '2026-03-20']),
  ])

  it('puts later days further right and keeps every day inside the drawing', () => {
    const xs = layout.rows[0].cells.map((c) => c.x)
    expect(xs).toEqual([...xs].sort((a, b) => a - b))
    expect(Math.min(...layout.rows.flatMap((r) => r.cells.map((c) => c.x)))).toBeGreaterThanOrEqual(92)
    expect(Math.max(...layout.rows.flatMap((r) => r.cells.map((c) => c.x)))).toBeLessThanOrEqual(1000)
  })

  it('places the same date at the same x in every row', () => {
    const a = layout.rows[0].cells[2].x
    const b = layout.rows[1].cells[1].x
    expect(a).toBeCloseTo(b, 6)
  })

  it('marks month starts', () => {
    expect(layout.months.map((m) => m.label)).toEqual(['Feb', 'Mar'])
  })

  it('finds the row under a y position and the nearest day', () => {
    expect(rowAt(layout, layout.rows[1].y + 3)).toBe(1)
    expect(rowAt(layout, -50)).toBe(-1)
    const flagged = layout.rows[0].cells[1]
    expect(nearestCell(layout.rows[0], flagged.x + 2).date).toBe('2026-02-10')
    expect(nearestCell(layout.rows[0], 5)).toBeNull()
  })
})

describe('sentiment helpers', () => {
  it('gauge angle runs from left to right', () => {
    expect(gaugeAngle(-1)).toBeCloseTo(Math.PI)
    expect(gaugeAngle(0)).toBeCloseTo(Math.PI / 2)
    expect(gaugeAngle(1)).toBeCloseTo(0)
  })

  it('confidence fills up to the number of headlines needed', () => {
    expect(confidenceRatio(7, 10)).toBe(0.7)
    expect(confidenceRatio(19, 10)).toBe(1)
  })

  it('status text matches the API statuses', () => {
    expect(statusInfo('ok').good).toBe(true)
    expect(statusInfo('low_confidence').text).toMatch(/Low confidence/)
    expect(statusInfo('unavailable').good).toBe(false)
  })

  it('only opens normal web links, never scripts', () => {
    expect(safeUrl('https://www.reuters.com/a?b=1')).toBe('https://www.reuters.com/a?b=1')
    expect(safeUrl('javascript:alert(1)')).toBeNull()
    expect(safeUrl('data:text/html,hi')).toBeNull()
    expect(safeUrl('not a url')).toBeNull()
  })
})

describe('sparkline', () => {
  it('starts at the first value and ends at the last, higher values are higher up', () => {
    const rising = sparkline([1, 2, 3], 100, 30)
    expect(rising.path.startsWith('M')).toBe(true)
    const falling = sparkline([3, 2, 1], 100, 30)
    expect(rising.end.y).toBeLessThan(falling.end.y)
  })

  it('does not break on a flat line or one value', () => {
    expect(sparkline([2, 2, 2], 100, 30).path).not.toMatch(/NaN/)
    expect(sparkline([2], 100, 30).path).not.toMatch(/NaN/)
  })
})
