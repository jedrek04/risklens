import { useMemo, useState } from 'react'
import RawNumbers from '../components/report/RawNumbers'
import ReportPaper from '../components/report/ReportPaper'
import ReportProgress from '../components/report/ReportProgress'
import Verification from '../components/report/Verification'
import '../components/report/report.css'
import { factIndex, flattenFacts, reportTexts, verifiedCount } from '../lib/report'

function Ready({ result, onAgain }) {
  const [view, setView] = useState('report')
  const [active, setActive] = useState(null)
  const [copied, setCopied] = useState(false)

  const facts = useMemo(() => flattenFacts(result.facts), [result])
  const index = useMemo(() => factIndex(facts), [facts])
  const counts = useMemo(() => verifiedCount(reportTexts(result.report), index), [result, index])

  const copy = () => {
    navigator.clipboard?.writeText(result.markdown)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <div className="report-grid">
      <div>
        <div className="seg" role="group" aria-label="View">
          <button aria-pressed={view === 'report'} onClick={() => setView('report')}>Report</button>
          <button aria-pressed={view === 'raw'} onClick={() => setView('raw')}>Raw numbers</button>
        </div>
        {view === 'report' ? (
          <div className="paper-wrap"><ReportPaper result={result} index={index} onHover={setActive} /></div>
        ) : (
          <RawNumbers facts={facts} />
        )}
      </div>
      <aside className="side">
        <Verification result={result} counts={counts} facts={facts} active={active} />
        <div className="card actions">
          <button className="btn primary" onClick={() => window.print()}>Download PDF</button>
          <button className="btn" onClick={copy}>{copied ? 'Copied ✓' : 'Copy text'}</button>
          <button className="btn ghost wide-btn" onClick={onAgain}>Write it again</button>
        </div>
      </aside>
    </div>
  )
}

export default function ReportPage({ analysis }) {
  const { report } = analysis

  return (
    <main>
      <div className="eyebrow">Step 3</div>
      <h1>Your report</h1>
      <p className="lede">Written by Gemini from the three models' results. Every number in the text is checked against the data before you see it.</p>

      {report.status === 'idle' && (
        <div className="card progress">
          <div>
            <b>Ready to write your report</b>
            <p className="muted small">It uses the numbers on the Analyse screen, so the report and the cards always match.</p>
          </div>
          <button className="btn primary" onClick={analysis.generateReport}>Generate report</button>
        </div>
      )}
      {report.status === 'loading' && <ReportProgress />}
      {report.status === 'error' && (
        <div className="card progress">
          <div>
            <b>The report could not be written</b>
            <p className="muted small">{report.error}</p>
          </div>
          <button className="btn" onClick={analysis.generateReport}>Try again</button>
        </div>
      )}
      {report.status === 'ok' && <Ready result={report.data} onAgain={analysis.generateReport} />}
    </main>
  )
}
