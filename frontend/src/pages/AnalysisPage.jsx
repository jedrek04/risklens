import Heatmap from '../components/analysis/Heatmap'
import SentimentSection from '../components/analysis/SentimentSection'
import UnusualDays from '../components/analysis/UnusualDays'
import VolatilityBars from '../components/analysis/VolatilityBars'
import FanChart from '../components/analysis/FanChart'
import Card from '../components/analysis/Card'
import KpiTiles from '../components/analysis/KpiTiles'
import RiskShare from '../components/analysis/RiskShare'
import SummaryBar from '../components/analysis/SummaryBar'
import '../components/analysis/analysis.css'
import { HORIZON_CHOICES } from '../config'

function HorizonSwitch({ value, onChange }) {
  const choices = [...new Set([...HORIZON_CHOICES, value])].sort((a, b) => a - b)
  return (
    <div className="seg" role="group" aria-label="Horizon in days">
      {choices.map((h) => (
        <button key={h} aria-pressed={h === value} onClick={() => onChange(h)}>{h} d</button>
      ))}
    </div>
  )
}

export default function AnalysisPage({ analysis, onGenerate }) {
  const { request, items, risk } = analysis
  const slots = Object.fromEntries(items.map((i) => [i.symbol, i.slot]))
  const weights = Object.fromEntries(request.portfolio.map((p) => [p.ticker, `${Math.round(p.weight * 100)}%`]))
  const retryRisk = () => analysis.retry('risk')
  const finished = (state) => state.status === 'ok' || state.status === 'error'
  const canGenerate = risk.status === 'ok' && finished(analysis.anomalies) && finished(analysis.sentiment)

  return (
    <main>
      <div className="eyebrow">Step 2</div>
      <h1>Your portfolio analysis</h1>
      <SummaryBar items={items} weights={weights} analysis={analysis} />

      <KpiTiles risk={risk} onRetry={retryRisk} />

      <div className="grid-2">
        <Card
          title="Where the portfolio could end up"
          subtitle="simulated return by day"
          state={risk}
          wait="Simulating futures"
          onRetry={retryRisk}
          actions={<HorizonSwitch value={request.horizon} onChange={analysis.changeHorizon} />}
        >
          {risk.data && (
            <>
              <FanChart fan={risk.data.portfolio.fan_chart} />
              <p className="model-note">
                GARCH(1,1) volatility per asset, correlated shocks, {risk.data.meta.n_sim.toLocaleString('en-US')} simulations, zero expected drift.
              </p>
            </>
          )}
        </Card>
        <Card title="Where the risk comes from" state={risk} onRetry={retryRisk}>
          {risk.data && <RiskShare risk={risk.data} slots={slots} />}
        </Card>
      </div>

      <div className="grid-3">
        <Card title="How the assets move together" subtitle="correlation of daily returns" state={risk} onRetry={retryRisk}>
          {risk.data && <Heatmap correlation={risk.data.correlation} slots={slots} />}
        </Card>
        <Card title="Volatility by asset" subtitle="annualised, with the forecast" state={risk} onRetry={retryRisk}>
          {risk.data && <VolatilityBars assets={risk.data.assets} slots={slots} />}
        </Card>
      </div>

      <Card
        className="wide"
        title="Unusual days"
        subtitle="Isolation Forest, scored with only the data available before each day"
        state={analysis.anomalies}
        wait="Scoring every trading day · about 20 s"
        onRetry={() => analysis.retry('anomalies')}
      >
        {analysis.anomalies.data && <UnusualDays data={analysis.anomalies.data} slots={slots} />}
      </Card>

      <div className="eyebrow section-label">News tone · last 7 days · FinBERT</div>
      <SentimentSection state={analysis.sentiment} items={items} onRetry={() => analysis.retry('sentiment')} />

      <div className="card cta-bar">
        <div className="cta-text">
          <b>Ready for your written report?</b>
          <div className="muted">It uses the numbers above, so the report and the cards always match. About 7 seconds.</div>
        </div>
        <button className="btn primary" disabled={!canGenerate} onClick={onGenerate}>Generate report</button>
        {!canGenerate && <span className="muted small">Waiting for the analyses to finish</span>}
      </div>

      <p className="disclaimer">
        RiskLens gives statistical estimates for information only. It is not financial advice. Estimates can be wrong and past data does not predict future results.
      </p>
    </main>
  )
}
