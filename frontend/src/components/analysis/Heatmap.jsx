import { useState } from 'react'
import { colorOf } from '../../lib/colors'
import { correlationColor } from '../../lib/color'

const CELL = 62
const LEFT = 84
const TOP = 14

export default function Heatmap({ correlation, slots }) {
  const [hover, setHover] = useState(null)
  const { tickers, matrix } = correlation
  const n = tickers.length
  const width = LEFT + n * CELL + 10
  const height = TOP + n * CELL + 40

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="Correlation heatmap">
        {tickers.map((ticker, i) => (
          <g key={ticker} className="mono-label">
            <rect x="10" y={TOP + i * CELL + CELL / 2 - 5} width="10" height="10" rx="3" fill={colorOf(slots[ticker])} />
            <text x="26" y={TOP + i * CELL + CELL / 2 + 4} fill="#a8b2c4" fontSize="12">{ticker}</text>
            <text x={LEFT + i * CELL + CELL / 2} y={TOP + n * CELL + 16} textAnchor="middle" fill="#a8b2c4" fontSize="11">{ticker}</text>
          </g>
        ))}
        {matrix.map((row, i) =>
          row.map((value, j) => (
            <g key={`${i}-${j}`} onPointerMove={(e) => setHover({ i, j, left: e.clientX, top: e.clientY })} onPointerLeave={() => setHover(null)}>
              <rect
                x={LEFT + j * CELL + 1}
                y={TOP + i * CELL + 1}
                width={CELL - 2}
                height={CELL - 2}
                rx="5"
                fill={correlationColor(value)}
                stroke={hover && hover.i === i && hover.j === j ? '#e8ecf4' : 'none'}
              />
              <text
                x={LEFT + j * CELL + CELL / 2}
                y={TOP + i * CELL + CELL / 2 + 4}
                textAnchor="middle"
                fontSize="12.5"
                fontWeight="600"
                fill={Math.abs(value) > 0.55 ? '#fff' : '#e8ecf4'}
                className="mono-label"
              >
                {i === j ? '1' : value.toFixed(2)}
              </text>
            </g>
          )),
        )}
      </svg>
      {hover && (
        <div className="tip fixed" style={{ left: hover.left + 14, top: hover.top + 14 }}>
          <div className="tip-head">{tickers[hover.i]} and {tickers[hover.j]}</div>
          <div className="tip-row"><span>Correlation</span><b>{matrix[hover.i][hover.j].toFixed(2)}</b></div>
        </div>
      )}
      <div className="legend-row center">
        <span>−1 move opposite</span>
        <span><i className="gradient" /></span>
        <span>+1 move together</span>
      </div>
    </div>
  )
}
