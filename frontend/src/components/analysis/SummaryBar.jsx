import { colorOf } from '../../lib/colors'
import { seconds } from '../../lib/format'

const PILLS = [
  { name: 'risk', label: 'Risk' },
  { name: 'sentiment', label: 'Sentiment' },
  { name: 'anomalies', label: 'Unusual days' },
]

function Pill({ label, state, onRetry }) {
  if (state.status === 'error') {
    return (
      <span className="pill bad">
        ✕ {label} failed
        <button className="link" onClick={onRetry}>Retry</button>
      </span>
    )
  }
  const done = state.status === 'ok'
  return (
    <span className={done ? 'pill' : 'pill wait'}>
      <span className="tick">{done ? '✓' : '…'}</span>
      {label}
      {done && <b className="mono">{seconds(state.seconds)}</b>}
    </span>
  )
}

export default function SummaryBar({ items, weights, analysis }) {
  return (
    <div className="summary-bar">
      {items.map((item) => (
        <span key={item.symbol} className="pchip">
          <i className="dot" style={{ background: colorOf(item.slot) }} />
          <b>{item.symbol}</b>
          {weights[item.symbol]}
        </span>
      ))}
      <span className="grow" />
      {PILLS.map(({ name, label }) => (
        <Pill key={name} label={label} state={analysis[name]} onRetry={() => analysis.retry(name)} />
      ))}
    </div>
  )
}
