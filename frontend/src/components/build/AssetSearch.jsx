import { useMemo, useState } from 'react'
import { MAX_ASSETS } from '../../config'
import { GROUPS, categoryLabel } from '../../lib/groups'
import { groupCounts, searchAssets } from '../../lib/search'

const SHOWN = 40

export default function AssetSearch({ assets, selected, onAdd }) {
  const [query, setQuery] = useState('')
  const [group, setGroup] = useState('all')

  const counts = useMemo(() => groupCounts(assets), [assets])
  const results = useMemo(() => searchAssets(assets, query, group), [assets, query, group])
  const full = selected.length >= MAX_ASSETS

  return (
    <div className="card">
      <div className="card-head">
        <h2>Add assets</h2>
        <span className="sub">
          {results.length} {results.length === 1 ? 'match' : 'matches'}
          {results.length > SHOWN ? `, showing ${SHOWN}` : ''}
        </span>
      </div>

      <div className="search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" />
        </svg>
        <input
          type="search"
          placeholder="Search by name or ticker: Bayer, XOM, gold, Bitcoin"
          autoComplete="off"
          aria-label="Search assets"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      <div className="chips">
        {GROUPS.map((g) => (
          <button key={g.id} className="chip" aria-pressed={group === g.id} onClick={() => setGroup(g.id)}>
            {g.label}
            <small>{counts[g.id] ?? 0}</small>
          </button>
        ))}
      </div>

      <div className="results">
        {results.length === 0 && <div className="empty">No asset matches that search. Try a company name or a ticker.</div>}
        {results.slice(0, SHOWN).map((asset) => {
          const added = selected.includes(asset.symbol)
          return (
            <button key={asset.symbol} className="result" disabled={added || full} onClick={() => onAdd(asset.symbol)}>
              <span className="sym">{asset.symbol}</span>
              <span className="nm">{asset.name}</span>
              <span className="tag">{categoryLabel(asset.category)}</span>
              <span className={added ? 'add-label done' : 'add-label'}>{added ? 'Added ✓' : full ? '' : '+ Add'}</span>
            </button>
          )
        })}
      </div>

      <p className={full ? 'note warn' : 'note'}>
        {full
          ? `You have ${MAX_ASSETS} assets, the maximum. Remove one to add another.`
          : `Up to ${MAX_ASSETS} assets, so each one keeps its own colour.`}
      </p>
    </div>
  )
}
