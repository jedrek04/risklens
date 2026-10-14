// how much of the portfolio risk each asset brings, from the weights, volatilities and correlations the API returned
export function riskShares(risk) {
  const { tickers, matrix } = risk.correlation
  const byTicker = Object.fromEntries(risk.assets.map((a) => [a.ticker, a]))
  const weight = tickers.map((t) => byTicker[t].weight)
  const vol = tickers.map((t) => byTicker[t].annualized_vol)
  const covariance = (i, j) => matrix[i][j] * vol[i] * vol[j]

  let variance = 0
  for (let i = 0; i < tickers.length; i++) {
    for (let j = 0; j < tickers.length; j++) variance += weight[i] * weight[j] * covariance(i, j)
  }

  return tickers.map((ticker, i) => {
    let pull = 0
    for (let j = 0; j < tickers.length; j++) pull += covariance(i, j) * weight[j]
    return { ticker, weight: weight[i], share: (weight[i] * pull) / variance }
  })
}
