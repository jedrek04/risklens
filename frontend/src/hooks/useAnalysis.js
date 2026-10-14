import { useCallback, useRef, useState } from 'react'
import { fetchAnomalies, fetchRisk, fetchSentiment } from '../api'

const idle = { status: 'idle', data: null, error: null, seconds: null, refreshing: false }

const CALLS = { risk: fetchRisk, anomalies: fetchAnomalies, sentiment: fetchSentiment }

// runs the three analyses side by side. each one has its own state, so a slow or failed one never blocks the others.
export default function useAnalysis() {
  const [request, setRequest] = useState(null)
  const [items, setItems] = useState([])
  const [state, setState] = useState({ risk: idle, anomalies: idle, sentiment: idle })
  const latest = useRef({ risk: 0, anomalies: 0, sentiment: 0 })

  const update = (name, change) => setState((s) => ({ ...s, [name]: { ...s[name], ...change } }))

  const load = useCallback((name, req, keepData) => {
    const id = ++latest.current[name]
    setState((s) => ({
      ...s,
      [name]: keepData && s[name].data
        ? { ...s[name], refreshing: true, error: null }
        : { ...idle, status: 'loading' },
    }))

    CALLS[name](req)
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
    for (const name of Object.keys(CALLS)) load(name, req, false)
  }, [load])

  // a new horizon only needs the risk numbers again, the old chart stays visible meanwhile
  const changeHorizon = useCallback((horizon) => {
    const req = { ...request, horizon }
    setRequest(req)
    load('risk', req, true)
  }, [request, load])

  const retry = useCallback((name) => load(name, request, false), [request, load])

  return { request, items, ...state, start, changeHorizon, retry }
}
