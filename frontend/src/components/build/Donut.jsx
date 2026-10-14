import { colorOf } from '../../lib/colors'
import { totalWeight } from '../../lib/portfolio'

const SIZE = 170
const RADIUS = 64
const STROKE = 22
const GAP = 2.5

export default function Donut({ items }) {
  const circumference = 2 * Math.PI * RADIUS
  const scale = Math.max(totalWeight(items), 100)
  let offset = 0

  const arcs = items
    .filter((item) => item.weight > 0)
    .map((item) => {
      const share = item.weight / scale
      const length = Math.max(0, share * circumference - GAP)
      const arc = { item, length, start: offset }
      offset += share
      return arc
    })

  const center = SIZE / 2

  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} role="img" aria-label="Portfolio weights">
      <circle cx={center} cy={center} r={RADIUS} fill="none" stroke="#1a2030" strokeWidth={STROKE} />
      {arcs.map(({ item, length, start }) => (
        <circle
          key={item.symbol}
          cx={center}
          cy={center}
          r={RADIUS}
          fill="none"
          stroke={colorOf(item.slot)}
          strokeWidth={STROKE}
          strokeDasharray={`${length} ${circumference - length}`}
          strokeDashoffset={circumference * 0.25 - start * circumference}
        />
      ))}
      <text x={center} y={center - 2} textAnchor="middle" fill="#e8ecf4" fontSize="24" fontWeight="800">
        {totalWeight(items).toFixed(1)}%
      </text>
      <text x={center} y={center + 18} textAnchor="middle" fill="#8490a5" fontSize="11.5">
        allocated
      </text>
    </svg>
  )
}
