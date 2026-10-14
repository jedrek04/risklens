import { colorOf } from '../../lib/colors'
import { percent } from '../../lib/format'
import { riskShares } from '../../lib/riskShare'

export default function RiskShare({ risk, slots }) {
  const rows = riskShares(risk).sort((a, b) => b.share - a.share)
  const widest = Math.max(...rows.map((r) => Math.max(r.weight, r.share)))
  const top = rows[0]
  const barWidth = (value) => `${(Math.max(value, 0) / widest) * 55}%`

  return (
    <>
      {rows.map((row) => (
        <div key={row.ticker} className="share-row">
          <div className="who">
            <i className="dot" style={{ background: colorOf(slots[row.ticker]) }} />
            {row.ticker}
          </div>
          <div className="bars">
            <div className="bar weight" title={`Share of your money in ${row.ticker}`}>
              <i style={{ width: barWidth(row.weight) }} />
              <span>{percent(row.weight, 0)} of money</span>
            </div>
            <div className="bar" title={`Share of the portfolio risk that comes from ${row.ticker}`}>
              <i style={{ width: barWidth(row.share), background: colorOf(slots[row.ticker]) }} />
              <span className="strong">{percent(row.share, 0)} of risk</span>
            </div>
          </div>
        </div>
      ))}
      <div className="insight">
        <b>{top.ticker}</b> holds {percent(top.weight, 0)} of the money and brings {percent(top.share, 0)} of the portfolio risk.
      </div>
    </>
  )
}
