import { useId } from 'react'
import { gaugeAngle } from '../../lib/sentiment'

const W = 240
const H = 130
const CX = 120
const CY = 118
const R = 92

const point = (score, radius = R) => ({ x: CX + radius * Math.cos(gaugeAngle(score)), y: CY - radius * Math.sin(gaugeAngle(score)) })

export default function Gauge({ score, faded }) {
  const gradient = useId()
  const start = point(-1)
  const end = point(1)
  const marker = score == null ? null : point(score)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="220" role="img" aria-label="Tone of the news from minus 1 to plus 1">
      <defs>
        <linearGradient id={gradient} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#e66767" />
          <stop offset="0.5" stopColor="#383835" />
          <stop offset="1" stopColor="#3987e5" />
        </linearGradient>
      </defs>
      <path
        d={`M${start.x} ${start.y} A${R} ${R} 0 0 1 ${end.x} ${end.y}`}
        fill="none"
        stroke={`url(#${gradient})`}
        strokeWidth="14"
        strokeLinecap="round"
        opacity={faded ? 0.25 : 1}
      />
      {[[-1, '−1'], [0, '0'], [1, '+1']].map(([value, label]) => {
        const p = point(value, R + 19)
        return <text key={label} x={p.x} y={value === 0 ? p.y - 4 : p.y + 12} textAnchor="middle" fill="#8490a5" fontSize="11">{label}</text>
      })}
      {marker && <circle cx={marker.x} cy={marker.y} r="9" fill="#e8ecf4" stroke="#121722" strokeWidth="3" />}
    </svg>
  )
}
