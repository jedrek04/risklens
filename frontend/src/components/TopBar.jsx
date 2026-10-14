const STEPS = [
  { id: 'build', label: 'Build' },
  { id: 'analyse', label: 'Analyse' },
  { id: 'report', label: 'Report' },
]

export default function TopBar({ step, enabled, onStep }) {
  return (
    <header className="top">
      <div className="top-inner">
        <div className="brand">
          <svg viewBox="0 0 22 22" width="22" height="22" aria-hidden="true">
            <path d="M2 15 C8 15 12 11 20 4 L20 19 C12 19 8 18 2 17 Z" fill="#3987e5" opacity=".25" />
            <path d="M2 15 C8 14.5 12 12 20 8.5" stroke="#8fb4ff" strokeWidth="2" fill="none" strokeLinecap="round" />
          </svg>
          RiskLens
        </div>
        <nav className="steps" aria-label="Steps">
          {STEPS.map((s, i) => (
            <button
              key={s.id}
              className="step"
              aria-current={step === s.id ? 'page' : undefined}
              disabled={!enabled[s.id]}
              onClick={() => onStep(s.id)}
            >
              <b>{i + 1}</b>
              <span>{s.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}
