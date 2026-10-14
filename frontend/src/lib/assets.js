import tickers from '../data/tickers.json'

export const ASSETS = tickers
export const ASSETS_BY_SYMBOL = Object.fromEntries(tickers.map((t) => [t.symbol, t]))
export const nameOf = (symbol) => ASSETS_BY_SYMBOL[symbol]?.name ?? symbol
