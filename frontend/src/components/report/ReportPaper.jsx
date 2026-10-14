import { annotate } from '../../lib/report'

// a text where every number that exists in the data is underlined and linked to its fact
function Text({ text, index, onHover }) {
  return annotate(text, index).map((part, i) =>
    part.fact === null ? (
      part.text
    ) : (
      <span key={i} className="num" onPointerEnter={() => onHover(part.fact)} onPointerLeave={() => onHover(null)}>
        {part.text}
      </span>
    ),
  )
}

export default function ReportPaper({ result, index, onHover }) {
  const { report, facts, disclaimer, meta } = result
  const risk = facts.risk
  const text = (value) => <Text text={value} index={index} onHover={onHover} />

  return (
    <article className="paper" id="paper">
      <div className="paper-brand">
        <b>RISKLENS</b>
        <span>Portfolio risk report</span>
      </div>
      <h1>{text(report.title)}</h1>

      <div className="paper-stats">
        {[
          [`Value at Risk, ${risk.confidence}, ${risk.horizon_days} days`, risk.var],
          ['Expected shortfall', risk.cvar],
          ['Portfolio volatility', risk.portfolio_volatility],
        ].map(([label, value]) => (
          <div key={label} className="paper-stat">
            <div className="v">{value}</div>
            <div className="l">{label}</div>
          </div>
        ))}
      </div>

      <table>
        <thead>
          <tr><th>Holding</th><th className="n">Weight</th><th className="n">Annualised volatility</th></tr>
        </thead>
        <tbody>
          {risk.assets.map((a) => (
            <tr key={a.ticker}>
              <td>{a.name} <span className="paper-ticker">{a.ticker}</span></td>
              <td className="n">{a.weight}</td>
              <td className="n">{a.annualized_volatility}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {report.sections.map((section) => (
        <section key={section.heading}>
          <h2>{section.heading}</h2>
          <p>{text(section.body)}</p>
          {section.bullets && <ul>{section.bullets.map((b) => <li key={b}>{text(b)}</li>)}</ul>}
        </section>
      ))}

      <div className="paper-foot">{disclaimer}</div>
      <div className="paper-meta">Generated {meta.generated_at.slice(0, 16).replace('T', ' ')} UTC with {meta.model}.</div>
    </article>
  )
}
