import { colorOf } from '../../lib/colors'
import { isComplete, remainingWeight, totalWeight } from '../../lib/portfolio'

export default function TotalBar({ items }) {
  const total = totalWeight(items)
  const remaining = remainingWeight(items)
  const complete = isComplete(items)
  const scale = Math.max(total, 100)

  let message = ''
  if (!complete && items.length > 0) {
    message = remaining > 0 ? `${remaining.toFixed(2)}% still to allocate` : `${Math.abs(remaining).toFixed(2)}% too much`
  }

  return (
    <>
      <div className="total-bar" aria-hidden="true">
        {items.filter((i) => i.weight > 0).map((i) => (
          <i key={i.symbol} style={{ width: `${(i.weight / scale) * 100}%`, background: colorOf(i.slot) }} />
        ))}
      </div>
      <div className="total-row">
        <span className="big mono">{total.toFixed(2)}%</span>
        <span className={complete ? 'state ok' : 'state bad'}>
          {complete ? '✓ Ready' : remaining < 0 ? '⚠ Over 100%' : '⚠ Not 100% yet'}
        </span>
        <span className="muted">{message}</span>
      </div>
    </>
  )
}
