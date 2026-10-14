import { API_URL } from './config'

export class ApiError extends Error {}

// turns what the server said into a sentence a person can act on
export function friendlyError(status, body) {
  if (status === 400 && typeof body?.detail === 'string') return body.detail
  if (status === 422) return 'Some input is not valid. Check the weights and the model settings.'
  if (status === 403 || status === 401) return 'The API refused the request. It may need a sign-in.'
  return 'The server had a problem. Please try again.'
}

async function post(path, body) {
  const started = performance.now()
  let response

  try {
    response = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ApiError('Cannot reach the API. Check your connection and, in development, that you are logged in with gcloud.')
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(friendlyError(response.status, detail))
  }

  return { data: await response.json(), seconds: (performance.now() - started) / 1000 }
}

export const fetchRisk = (request) => post('/risk/portfolio', request)
export const fetchAnomalies = (request) => post('/risk/anomalies', { portfolio: request.portfolio })
export const fetchSentiment = (request) => post('/risk/sentiment', { portfolio: request.portfolio })

export const fetchReport = ({ portfolio, risk, anomalies, sentiment }) =>
  post('/risk/report', { portfolio, risk, anomalies, sentiment })
