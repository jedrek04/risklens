import { fillRemaining, remainingWeight, removeAsset, setWeight } from '../../lib/portfolio'
import PortfolioRow from './PortfolioRow'

export default function PortfolioTable({ items, assetsBySymbol, onChange }) {
  const remaining = remainingWeight(items)

  if (items.length === 0) {
    return (
      <div className="empty-portfolio">
        <b>No assets yet</b>
        Pick your first asset from the list on the left.
      </div>
    )
  }

  return (
    <div>
      {items.map((item) => (
        <PortfolioRow
          key={item.symbol}
          item={item}
          asset={assetsBySymbol[item.symbol]}
          remaining={remaining}
          onWeight={(weight) => onChange(setWeight(items, item.symbol, weight))}
          onFill={() => onChange(fillRemaining(items, item.symbol))}
          onRemove={() => onChange(removeAsset(items, item.symbol))}
        />
      ))}
    </div>
  )
}
