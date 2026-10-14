export default function AnalysisPage({ request }) {
  return (
    <main>
      <div className="eyebrow">Step 2</div>
      <h1>Your portfolio analysis</h1>
      <p className="lede">This screen is built next. For now it shows what the Build step will send to the backend.</p>
      <div className="card">
        <h2 style={{ marginBottom: 10 }}>Request for the risk, anomaly and sentiment calls</h2>
        <pre className="mono" style={{ margin: 0, overflow: 'auto', color: 'var(--text-2)' }}>{JSON.stringify(request, null, 2)}</pre>
      </div>
    </main>
  )
}
