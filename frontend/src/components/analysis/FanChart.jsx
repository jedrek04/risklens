import { useMemo, useState } from 'react'
import { niceTicks, tickDecimals } from '../../lib/chart'
import { percent } from '../../lib/format'

const W = 760
const H = 300
const MARGIN = { left: 54, right: 92, top: 16, bottom: 34 }
const BLUE = '#3987e5'

const ROWS = [
  ['p95', '95th percentile', 'rgba(57,135,229,.5)'],
  ['p75', '75th percentile', 'rgba(57,135,229,.8)'],
  ['p50', 'Median', BLUE],
  ['p25', '25th percentile', 'rgba(57,135,229,.8)'],
  ['p5', '5th percentile', 'rgba(57,135,229,.5)'],
]

export default function FanChart({ fan }) {
  const [hover, setHover] = useState(null)

  const chart = useMemo(() => {
    const days = [0, ...fan.day]
    const series = Object.fromEntries(['p5', 'p25', 'p50', 'p75', 'p95'].map((k) => [k, [0, ...fan[k]]]))
    const low = Math.min(...series.p5)
    const high = Math.max(...series.p95)
    const pad = (high - low) * 0.08
    const x = (d) => MARGIN.left + (d / days[days.length - 1]) * (W - MARGIN.left - MARGIN.right)
    const y = (v) => MARGIN.top + (1 - (v - (low - pad)) / (high - low + 2 * pad)) * (H - MARGIN.top - MARGIN.bottom)
    return { days, series, x, y, ticks: niceTicks(low - pad, high + pad) }
  }, [fan])

  const { days, series, x, y, ticks } = chart
  const decimals = tickDecimals(ticks)
  const last = days.length - 1
  const step = last <= 10 ? 1 : last <= 30 ? 5 : 15

  const line = (values) => values.map((v, i) => `${i ? 'L' : 'M'}${x(days[i])} ${y(v)}`).join('')
  const band = (top, bottom) =>
    `${line(top)}${bottom.map((_, i) => `L${x(days[last - i])} ${y(bottom[last - i])}`).join('')}Z`

  function onMove(e) {
    const box = e.currentTarget.ownerSVGElement.getBoundingClientRect()
    const px = ((e.clientX - box.left) / box.width) * W
    let best = 0
    days.forEach((d, i) => {
      if (Math.abs(x(d) - px) < Math.abs(x(days[best]) - px)) best = i
    })
    setHover({ index: best, left: e.clientX - box.left, top: e.clientY - box.top })
  }

  const tickLabels = []
  for (let d = 0; d <= last; d += step) tickLabels.push(d)

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Fan chart of simulated portfolio returns">
        {ticks.map((v) => (
          <g key={v}>
            <line x1={MARGIN.left} x2={W - MARGIN.right} y1={y(v)} y2={y(v)} stroke={v === 0 ? '#33405a' : '#1b2231'} />
            <text x={MARGIN.left - 10} y={y(v) + 4} textAnchor="end" className="axis">{percent(v, decimals, { sign: v > 0 })}</text>
          </g>
        ))}
        {tickLabels.map((d) => (
          <text key={d} x={x(d)} y={H - 10} textAnchor="middle" className="axis">{d === 0 ? 'today' : `day ${d}`}</text>
        ))}
        <path d={band(series.p95, series.p5)} fill="rgba(57,135,229,.16)" />
        <path d={band(series.p75, series.p25)} fill="rgba(57,135,229,.34)" />
        <path d={line(series.p50)} fill="none" stroke={BLUE} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        {['p95', 'p5'].map((k) => (
          <g key={k}>
            <circle cx={x(days[last])} cy={y(series[k][last])} r="4.5" fill={BLUE} stroke="#121722" strokeWidth="2" />
            <text x={x(days[last]) + 12} y={y(series[k][last]) + 4} fill="#e8ecf4" fontSize="12" fontWeight="700">
              {percent(series[k][last], 1, { sign: true })}
            </text>
          </g>
        ))}
        <text x={x(days[last]) + 12} y={y(series.p5[last]) + 19} fill="#8490a5" fontSize="11">Value at Risk</text>
        {hover && <line x1={x(days[hover.index])} x2={x(days[hover.index])} y1={MARGIN.top} y2={H - MARGIN.bottom} stroke="#8490a5" />}
        <rect
          x={MARGIN.left}
          y={MARGIN.top}
          width={W - MARGIN.left - MARGIN.right}
          height={H - MARGIN.top - MARGIN.bottom}
          fill="transparent"
          onPointerMove={onMove}
          onPointerLeave={() => setHover(null)}
        />
      </svg>

      {hover && (
        <div className="tip" style={{ left: hover.left + 14, top: hover.top + 14 }}>
          <div className="tip-head">{hover.index === 0 ? 'Today' : `Day ${days[hover.index]}`}</div>
          {ROWS.map(([key, label, color]) => (
            <div key={key} className="tip-row">
              <span><i className="tip-key" style={{ background: color }} />{label}</span>
              <b>{percent(series[key][hover.index], 1, { sign: true })}</b>
            </div>
          ))}
        </div>
      )}

      <div className="legend-row">
        <span><i style={{ background: 'rgba(57,135,229,.18)' }} />5th to 95th percentile</span>
        <span><i style={{ background: 'rgba(57,135,229,.38)' }} />25th to 75th</span>
        <span><i style={{ background: BLUE, height: 2 }} />Median</span>
      </div>
    </div>
  )
}
