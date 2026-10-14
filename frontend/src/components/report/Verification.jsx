import { useEffect, useRef } from 'react'
import { factLabel } from '../../lib/report'

export default function Verification({ result, counts, facts, active }) {
  const { meta, markdown } = result
  const list = useRef(null)

  useEffect(() => {
    if (active === null) return
    list.current?.querySelector(`[data-i="${active}"]`)?.scrollIntoView({ block: 'nearest' })
  }, [active])

  const words = markdown.trim().split(/\s+/).length
  const attempts = meta.attempts === 1 ? 'first attempt' : `${meta.attempts} attempts`

  return (
    <div className="card">
      <div className="card-head tight"><h2>Verification</h2></div>
      <div className="vrow"><span className="ok">✓</span><span><b>{counts.verified} of {counts.numbers} numbers</b> in the text were checked against the data, and all were found.</span></div>
      <div className="vrow"><span className="ok">✓</span><span>Written on the {attempts}{meta.rejected_draft_issues.length > 0 ? ', an earlier draft was rejected by the check.' : ', no draft was rejected.'}</span></div>
      <div className="vrow"><span className="ok">✓</span><span>No buy or sell advice and no risk labels. Recommendations are things to review.</span></div>
      <div className="vrow muted">Model {meta.model} · {words} words</div>

      <details className="settings">
        <summary>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2"><path d="m4 2 4 4-4 4" /></svg>
          Data behind this report
        </summary>
        <div className="fact-list" ref={list}>
          {facts.map((fact, i) => (
            <div key={i} data-i={i} className={active === i ? 'hit' : ''}>
              <span>{factLabel(fact.path)}</span>
              <span className="mono">{fact.value}</span>
            </div>
          ))}
        </div>
      </details>
    </div>
  )
}
