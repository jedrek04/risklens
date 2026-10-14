export const GROUPS = [
  { id: 'all', label: 'All' },
  { id: 'us', label: 'US stocks' },
  { id: 'europe', label: 'European stocks' },
  { id: 'asia', label: 'Asian stocks' },
  { id: 'etf', label: 'ETFs' },
  { id: 'crypto', label: 'Crypto' },
  { id: 'commodities', label: 'Commodities' },
  { id: 'indexes', label: 'Indexes' },
]

// exact category names as in backend/app/services/market_data/tickers.py
export const CATEGORY_LABELS = {
  crypto: 'Crypto',
  commodities: 'Commodity',
  market_indexes: 'Index',
  etf_broad: 'ETF · Broad market',
  etf_dividend: 'ETF · Dividend',
  etf_bonds: 'ETF · Bonds',
  etf_tech: 'ETF · Technology',
  etf_energy_materials: 'ETF · Energy and materials',
  etf_other_sectors: 'ETF · Other sectors',
  stocks_europe: 'Europe',
  stocks_asia: 'Asia',
  stocks_us_technology: 'US · Technology',
  stocks_us_finance: 'US · Finance',
  stocks_us_healthcare: 'US · Healthcare',
  stocks_us_consumer: 'US · Consumer',
  stocks_us_industrials: 'US · Industrials',
  stocks_us_energy: 'US · Energy',
  stocks_us_realestate: 'US · Real estate',
  stocks_us_utilities: 'US · Utilities',
  stocks_us_staples: 'US · Staples',
  stocks_us_telecom: 'US · Telecom',
  stocks_us_materials: 'US · Materials',
}

export function groupOf(category) {
  if (category.startsWith('stocks_us')) return 'us'
  if (category === 'stocks_europe') return 'europe'
  if (category === 'stocks_asia') return 'asia'
  if (category.startsWith('etf')) return 'etf'
  if (category === 'crypto') return 'crypto'
  if (category === 'commodities') return 'commodities'
  return 'indexes'
}

export const categoryLabel = (category) => CATEGORY_LABELS[category] ?? category
