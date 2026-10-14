import { useCallback, useRef, useState } from 'react'
import { fetchAnomalies, fetchReport, fetchRisk, fetchSentiment } from '../api'

const idle = { status: 'idle', data: null, error: null, seconds: null, refreshing: false }

const CALLS = { risk: fetchRisk, anomalies: fetchAnomalies, sentiment: fetchSentiment }

// runs the three analyses side by side, and the report that is written from their results.
// each has its own state, so a slow or failed one never blocks the others.
export default function useAnalysis() {
  const [request, setRequest] = useState(null)
  const [items, setItems] = useState([])
  const [state, setState] = useState({ risk: idle, anomalies: idle, sentiment: idle, report: idle })
  const latest = useRef({ risk: 0, anomalies: 0, sentiment: 0, report: 0 })

  const update = (name, change) => setState((s) => ({ ...s, [name]: { ...s[name], ...change } }))

  const run = useCallback((name, call, keepData) => {
    const id = ++latest.current[name]
    setState((s) => ({
      ...s,
      // a report belongs to the numbers it was written from, so any new numbers make it stale
      report: name === 'report' ? s.report : idle,
      [name]: keepData && s[name].data
        ? { ...s[name], refreshing: true, error: null }
        : { ...idle, status: 'loading' },
    }))

    call()
      .then(({ data, seconds }) => {
        if (latest.current[name] === id) update(name, { status: 'ok', data, seconds, error: null, refreshing: false })
      })
      .catch((error) => {
        if (latest.current[name] === id) update(name, { status: 'error', data: null, error: error.message, refreshing: false })
      })
  }, [])

  const start = useCallback((req, portfolioItems) => {
    setRequest(req)
    setItems(portfolioItems)
    for (const name of Object.keys(CALLS)) run(name, () => CALLS[name](req), false)
  }, [run])

  // a new horizon only needs the risk numbers again, the old chart stays visible meanwhile
  const changeHorizon = useCallback((horizon) => {
    const req = { ...request, horizon }
    setRequest(req)
    run('risk', () => fetchRisk(req), true)
  }, [request, run])

  const retry = useCallback((name) => run(name, () => CALLS[name](request), false), [request, run])

  const generateReport = useCallback(() => {
    run('report', () => fetchReport({
      portfolio: request.portfolio,
      risk: state.risk.data,
      anomalies: state.anomalies.data,
      sentiment: state.sentiment.data,
    }), false)
  }, [request, state, run])

  return { request, items, ...state, start, changeHorizon, retry, generateReport }
}
