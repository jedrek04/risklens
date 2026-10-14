import { colorOf } from '../../lib/colors'
import { percent } from '../../lib/format'
import Sparkline from './Sparkline'

export default function VolatilityBars({ assets, slots }) {
  const rows = [...assets].sort((a, b) => b.annualized_vol - a.annualized_vol)
  const widest = rows[0].annualized_vol

  return (
    <>
      <div className="vol-row head">
        <span />
        <span>Annualised volatility</span>
        <span>Daily forecast, next days</span>
      </div>
      {rows.map((asset) => {
        const color = colorOf(slots[asset.ticker])
        const forecast = asset.volatility.forecast
        return (
          <div key={asset.ticker} className="vol-row" title={`Daily volatility today: ${percent(asset.volatility.current, 2)}`}>
            <div className="who">
              <i className="dot" style={{ background: color }} />
              {asset.ticker}
            </div>
            <div className="bar">
              <i style={{ width: `${(asset.annualized_vol / widest) * 74}%`, background: color }} />
              <span className="strong">{percent(asset.annualized_vol, 1)}</span>
            </div>
            <div className="spark">
              <Sparkline values={forecast} color={color} />
              <span className="mono muted">{percent(forecast[0], 2)} → {percent(forecast[forecast.length - 1], 2)}</span>
            </div>
          </div>
        )
      })}
      <p className="model-note">GARCH expects volatility to drift back toward each asset's long-run level. Sorted from the most to the least volatile.</p>
    </>
  )
}
