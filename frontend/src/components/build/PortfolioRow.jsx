import { useEffect, useState } from 'react'
import { colorOf } from '../../lib/colors'

const droplet = (
  <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
    <path d="M8 1.5C8 1.5 3.2 6.6 3.2 10a4.8 4.8 0 0 0 9.6 0C12.8 6.6 8 1.5 8 1.5Z" />
  </svg>
)

function fillLabel(remaining) {
  if (Math.abs(remaining) < 0.005) return { text: '0%', hint: 'Weights already add up to 100%' }
  const amount = Math.abs(remaining)
  return remaining > 0
    ? { text: `+${amount}%`, hint: `Add the remaining ${amount}% here` }
    : { text: `−${amount}%`, hint: `Take the extra ${amount}% off here` }
}

export default function PortfolioRow({ item, asset, remaining, onWeight, onFill, onRemove }) {
  // keep what the person is typing as text, so "12." or an empty box does not jump around
  const [text, setText] = useState(String(item.weight))

  useEffect(() => {
    if (Number(text) !== item.weight) setText(String(item.weight))
  }, [item.weight])

  const fill = fillLabel(remaining)

  return (
    <div className="prow">
      <i className="dot" style={{ background: colorOf(item.slot) }} />
      <div className="pname">
        <b>{item.symbol}</b>
        <span>{asset?.name ?? item.symbol}</span>
      </div>
      <div className="num-input">
        <input
          type="number"
          min="0"
          max="100"
          step="0.01"
          aria-label={`Weight of ${item.symbol}`}
          value={text}
          onChange={(e) => {
            setText(e.target.value)
            onWeight(Number(e.target.value))
          }}
        />
        <span>%</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="0.5"
        aria-label={`Weight slider for ${item.symbol}`}
        value={Math.min(100, item.weight)}
        onChange={(e) => onWeight(Number(e.target.value))}
      />
      <button className="fill-btn" disabled={Math.abs(remaining) < 0.005} title={fill.hint} aria-label={fill.hint} onClick={onFill}>
        {droplet}
        <span>{fill.text}</span>
      </button>
      <button className="icon-btn" aria-label={`Remove ${item.symbol}`} onClick={onRemove}>
        <svg width="14" height="14" viewBox="0 0 14 14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
          <path d="m3 3 8 8M11 3l-8 8" />
        </svg>
      </button>
    </div>
  )
}
