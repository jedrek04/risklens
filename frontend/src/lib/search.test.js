import { describe, expect, it } from 'vitest'
import tickers from '../data/tickers.json'
import { CATEGORY_LABELS, groupOf } from './groups'
import { groupCounts, searchAssets } from './search'
import { validateSettings } from './settings'

describe('ticker data', () => {
  it('has all 707 assets, each with a known category', () => {
    expect(tickers).toHaveLength(707)
    for (const t of tickers) expect(CATEGORY_LABELS[t.category], t.symbol).toBeDefined()
  })

  it('group counts add up to the total', () => {
    const counts = groupCounts(tickers)
    const sum = Object.entries(counts).filter(([id]) => id !== 'all').reduce((s, [, n]) => s + n, 0)
    expect(sum).toBe(counts.all)
  })
})

describe('search', () => {
  it('finds by name and by ticker, case-insensitive', () => {
    expect(searchAssets(tickers, 'bayer', 'all').map((a) => a.symbol)).toContain('BAYN.DE')
    expect(searchAssets(tickers, 'xom', 'all')[0].symbol).toBe('XOM')
  })

  it('puts results that start with the text first', () => {
    const symbols = searchAssets(tickers, 'gold', 'all').map((a) => a.name.toLowerCase())
    expect(symbols[0].startsWith('gold')).toBe(true)
  })

  it('filters by group', () => {
    const crypto = searchAssets(tickers, '', 'crypto')
    expect(crypto).toHaveLength(18)
    expect(crypto.every((a) => groupOf(a.category) === 'crypto')).toBe(true)
  })

  it('mixes groups when there is no search text', () => {
    const first = searchAssets(tickers, '', 'all').slice(0, 7).map((a) => groupOf(a.category))
    expect(new Set(first).size).toBe(7)
  })

  it('returns nothing for text that matches nothing', () => {
    expect(searchAssets(tickers, 'zzzzqqq', 'all')).toEqual([])
  })
})

describe('model settings', () => {
  const ok = { horizon: 10, simulations: 10000, days: 730 }

  it('accepts the defaults and the limits', () => {
    expect(validateSettings(ok)).toEqual({})
    expect(validateSettings({ horizon: 90, simulations: 100000, days: 4000 })).toEqual({})
    expect(validateSettings({ horizon: 1, simulations: 1000, days: 150 })).toEqual({})
  })

  it('rejects values outside the limits, decimals and empty fields', () => {
    expect(Object.keys(validateSettings({ horizon: 91, simulations: 999, days: 4001 }))).toEqual(['horizon', 'simulations', 'days'])
    expect(validateSettings({ ...ok, horizon: 10.5 }).horizon).toBeDefined()
    expect(validateSettings({ ...ok, days: NaN }).days).toBeDefined()
  })
})
