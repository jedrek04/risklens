import { percent } from '../../lib/format'
import Card from './Card'
import InfoTip from './InfoTip'

export default function KpiTiles({ risk, onRetry }) {
  const data = risk.data
  const fan = data?.portfolio.fan_chart
  const last = fan ? fan.p5.length - 1 : 0

  return (
    <div className="kpis">
      <Card className="kpi hero" state={risk} wait="Running the simulation" onRetry={onRetry}>
        {data && (
          <>
            <div className="kpi-label">
              Value at Risk · {percent(data.meta.confidence, 0)} · {data.meta.horizon} days
              <InfoTip text="In 95 of 100 simulated futures the portfolio loses less than this over the horizon. It is an estimate from a model, not a guarantee." />
            </div>
            <div className="kpi-value">{percent(data.portfolio.var)}</div>
            <div className="kpi-note">In 95 of 100 simulated outcomes the loss is smaller than this.</div>
          </>
        )}
      </Card>
      <Card className="kpi" state={risk} onRetry={onRetry}>
        {data && (
          <>
            <div className="kpi-label">
              Expected shortfall
              <InfoTip text="The average loss in the worst 5 of 100 simulated outcomes, the ones beyond the Value at Risk." />
            </div>
            <div className="kpi-value">{percent(data.portfolio.cvar)}</div>
            <div className="kpi-note">Average of the worst 5%</div>
          </>
        )}
      </Card>
      <Card className="kpi" state={risk} onRetry={onRetry}>
        {data && (
          <>
            <div className="kpi-label">
              Portfolio volatility
              <InfoTip text="How widely the portfolio return is spread over the horizon (one standard deviation)." />
            </div>
            <div className="kpi-value">{percent(data.portfolio.volatility)}</div>
            <div className="kpi-note">Over the horizon</div>
          </>
        )}
      </Card>
      <Card className="kpi" state={risk} onRetry={onRetry}>
        {data && (
          <>
            <div className="kpi-label">
              Likely range
              <InfoTip text="Between the 5th and the 95th percentile of simulated outcomes: 90 of 100 futures end inside this range." />
            </div>
            <div className="kpi-value small">
              {percent(fan.p5[last], 1)} to {percent(fan.p95[last], 1, { sign: true })}
            </div>
            <div className="kpi-note">90 of 100 outcomes</div>
          </>
        )}
      </Card>
    </div>
  )
}
