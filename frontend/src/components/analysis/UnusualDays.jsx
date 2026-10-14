import { useMemo, useState } from 'react'
import { colorOf } from '../../lib/colors'
import { QUIET_DAY, unusualColor } from '../../lib/color'
import { calendarLayout, nearestCell, ROW_HEIGHT, rowAt, WIDTH } from '../../lib/calendar'
import { percent } from '../../lib/format'
import AnomalyDetail from './AnomalyDetail'
import Drawer from './Drawer'

const PORTFOLIO_COLOR = '#e6ecf8'
const longDate = (date) =>
  new Date(`${date}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })

export default function UnusualDays({ data, slots }) {
  const [hover, setHover] = useState(null)
  const [selected, setSelected] = useState(null)

  const rows = useMemo(
    () => [
      { name: 'Portfolio', color: PORTFOLIO_COLOR, series: data.portfolio },
      ...data.assets.map((series) => ({ name: series.name, color: colorOf(slots[series.name]), series })),
    ].map((row) => ({ ...row, dates: row.series.dates, scores: row.series.scores, anomaly: row.series.anomaly })),
    [data, slots],
  )
  const layout = useMemo(() => calendarLayout(rows), [rows])

  const detailOf = (row, date) => row.series.anomalies.find((a) => a.date === date)

  function find(e) {
    const box = e.currentTarget.getBoundingClientRect()
    const x = ((e.clientX - box.left) / box.width) * WIDTH
    const y = ((e.clientY - box.top) / box.height) * layout.height
    const index = rowAt(layout, y)
    if (index < 0) return null
    const cell = nearestCell(layout.rows[index], x)
    return cell ? { index, cell } : null
  }

  function onMove(e) {
    const found = find(e)
    setHover(found && { ...found, left: e.clientX, top: e.clientY })
  }

  function onClick(e) {
    const found = find(e)
    if (!found || !found.cell.flag) return
    const row = layout.rows[found.index]
    const detail = detailOf(row, found.cell.date)
    if (detail) setSelected({ rowName: row.name, date: found.cell.date, detail })
  }

  const hovered = hover && layout.rows[hover.index]
  const hoveredDetail = hover && hovered && hover.cell.flag ? detailOf(hovered, hover.cell.date) : null

  return (
    <>
      <div className="cal-key">
        <span>Normal day <i className="swatch" /></span>
        <span>Unusual <span className="ramp" /> stronger</span>
        <span className="muted">Click an unusual day to see why.</span>
      </div>
      <div className="cal">
        <svg
          viewBox={`0 0 ${WIDTH} ${layout.height}`}
          width="100%"
          role="img"
          aria-label="Calendar of unusual days"
          style={{ cursor: hover?.cell.flag ? 'pointer' : 'default' }}
          onPointerMove={onMove}
          onPointerLeave={() => setHover(null)}
          onClick={onClick}
        >
          {layout.months.map((m) => (
            <g key={m.x}>
              <line x1={m.x} x2={m.x} y1="18" y2={layout.height} stroke="#1b2231" />
              <text x={m.x + 4} y="12" fill="#8490a5" fontSize="11">{m.label}</text>
            </g>
          ))}
          {layout.rows.map((row) => (
            <g key={row.name}>
              <rect x="0" y={row.y + ROW_HEIGHT / 2 - 5} width="10" height="10" rx="3" fill={row.color} />
              <text x="16" y={row.y + ROW_HEIGHT / 2 + 4} fill="#a8b2c4" fontSize="12" fontWeight="600" className="mono-label">{row.name}</text>
              {row.cells.map((cell) => (
                <rect
                  key={cell.date}
                  x={cell.x - layout.cellWidth / 2}
                  y={row.y}
                  width={layout.cellWidth}
                  height={ROW_HEIGHT}
                  rx="1"
                  fill={cell.flag ? unusualColor(cell.score) : QUIET_DAY}
                />
              ))}
            </g>
          ))}
          {hover && <rect x={hover.cell.x - 1} y={hovered.y} width="2" height={ROW_HEIGHT} fill="#fff" pointerEvents="none" />}
        </svg>
      </div>

      {hover && (
        <div className="tip fixed" style={{ left: hover.left + 14, top: hover.top + 14 }}>
          <div className="tip-head">{hovered.name} · {longDate(hover.cell.date)}</div>
          <div className="tip-row"><span>Status</span><b>{hover.cell.flag ? 'Unusual' : 'Normal'}</b></div>
          {hover.cell.flag && <div className="tip-row"><span>Strength</span><b>{hover.cell.score.toFixed(3)}</b></div>}
          {hoveredDetail && <div className="tip-row"><span>Day return</span><b>{percent(hoveredDetail.return, 2, { sign: true })}</b></div>}
          {hover.cell.flag && <div className="tip-hint">Click to see why</div>}
        </div>
      )}

      <div className="counts">
        {rows.map((row) => (
          <span key={row.name}>{row.name} <b>{row.series.summary.anomalies} of {row.series.summary.scored_days}</b></span>
        ))}
      </div>

      <Drawer open={selected !== null} onClose={() => setSelected(null)}>
        {selected && <AnomalyDetail {...selected} />}
      </Drawer>
    </>
  )
}
