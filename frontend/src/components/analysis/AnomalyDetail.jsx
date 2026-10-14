import { percent } from '../../lib/format'

const NAMES = { return: 'Day return', volatility_5d: '5-day volatility', volatility_20d: '20-day volatility', volume_ratio: 'Trading volume' }
const MAX_Z = 6

const longDate = (date) =>
  new Date(`${date}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })

export default function AnomalyDetail({ rowName, date, detail }) {
  return (
    <>
      <div className="eyebrow">Why was this day unusual?</div>
      <h3>{rowName} · {longDate(date)}</h3>
      <p className="lede tight">
        The day return was <b>{percent(detail.return, 2, { sign: true })}</b>. Bars show how far each measure was from its recent normal, in standard deviations.
      </p>
      {Object.entries(detail.z_scores).map(([key, z]) => (
        <div key={key} className="z-row">
          <span>{NAMES[key] ?? key}</span>
          <div className="z-track">
            <i
              style={{
                width: `${Math.min(50, (Math.abs(z) / MAX_Z) * 50)}%`,
                [z >= 0 ? 'left' : 'right']: '50%',
                background: z >= 0 ? '#3987e5' : '#e66767',
              }}
            />
          </div>
          <b className="mono">{z < 0 ? '−' : '+'}{Math.abs(z).toFixed(1)}σ</b>
        </div>
      ))}
      <div className="insight">A value beyond about 3σ is rare on a normal day. The model flags a day when several measures are unusual together.</div>
      <p className="note">News for this day is not shown: the news source only covers the last 7 days.</p>
    </>
  )
}
