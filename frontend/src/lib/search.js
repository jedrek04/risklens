import { groupOf } from './groups'

const GROUP_ORDER = ['us', 'europe', 'asia', 'etf', 'crypto', 'commodities', 'indexes']

// with no search text, mix the groups so the first results are varied
function interleave(assets) {
  const byGroup = Object.fromEntries(GROUP_ORDER.map((id) => [id, []]))
  for (const asset of assets) byGroup[groupOf(asset.category)].push(asset)

  const mixed = []
  for (let i = 0; mixed.length < assets.length; i++) {
    for (const id of GROUP_ORDER) {
      if (byGroup[id][i]) mixed.push(byGroup[id][i])
    }
  }
  return mixed
}

export function searchAssets(assets, query, group) {
  const q = query.trim().toLowerCase()
  const inGroup = group === 'all' ? assets : assets.filter((a) => groupOf(a.category) === group)

  if (!q) return group === 'all' ? interleave(inGroup) : inGroup

  const matches = inGroup.filter((a) => a.symbol.toLowerCase().includes(q) || a.name.toLowerCase().includes(q))
  const startsWith = (a) => a.symbol.toLowerCase().startsWith(q) || a.name.toLowerCase().startsWith(q)
  return [...matches.filter(startsWith), ...matches.filter((a) => !startsWith(a))]
}

export function groupCounts(assets) {
  const counts = { all: assets.length }
  for (const asset of assets) {
    const id = groupOf(asset.category)
    counts[id] = (counts[id] ?? 0) + 1
  }
  return counts
}
