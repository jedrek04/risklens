import { useEffect, useState } from 'react'

export default function ReportProgress() {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setElapsed((s) => s + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="card progress">
      <div className="spinner" aria-hidden="true" />
      <div>
        <b>Writing your report…</b>
        <p className="muted small">
          {elapsed < 15 ? 'This usually takes about 7 seconds.' : 'This is taking longer than usual, but it is still working.'} ({elapsed} s)
        </p>
      </div>
    </div>
  )
}
