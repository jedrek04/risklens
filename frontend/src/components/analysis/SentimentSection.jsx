import Card from './Card'
import SentimentCard from './SentimentCard'

export default function SentimentSection({ state, items, onRetry }) {
  const slots = Object.fromEntries(items.map((i) => [i.symbol, i.slot]))

  if (state.status === 'error') return <Card state={state} onRetry={onRetry} />

  // while loading there is no data yet, so show one empty card per asset
  const assets = state.data ? state.data.assets : items.map((i) => ({ ticker: i.symbol }))

  return (
    <div className="sent-grid">
      {assets.map((asset) => (
        <Card key={asset.ticker} className="sc" state={state} wait="Reading headlines">
          {state.data && <SentimentCard asset={asset} slot={slots[asset.ticker]} needed={state.data.meta.min_headlines} />}
        </Card>
      ))}
    </div>
  )
}
