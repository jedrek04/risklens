import { describe, expect, it } from 'vitest'
import { MAX_ASSETS } from '../config'
import {
  addAsset, fillRemaining, isComplete, nextFreeSlot, remainingWeight, removeAsset, setWeight, toRequestPortfolio, totalWeight,
} from './portfolio'

const build = (...pairs) => pairs.reduce((items, [symbol, weight]) => setWeight(addAsset(items, symbol), symbol, weight), [])

describe('portfolio weights', () => {
  it('a new asset takes the weight that is still free', () => {
    const items = build(['AAPL', 60])
    expect(addAsset(items, 'MSFT').at(-1).weight).toBe(40)
  })

  it('the first asset starts at 100 and later ones at 0 when nothing is free', () => {
    const items = addAsset([], 'AAPL')
    expect(items[0].weight).toBe(100)
    expect(addAsset(items, 'MSFT').at(-1).weight).toBe(0)
  })

  it('is only complete at exactly 100', () => {
    expect(isComplete([])).toBe(false)
    expect(isComplete(build(['A', 60], ['B', 39.99]))).toBe(false)
    expect(isComplete(build(['A', 60], ['B', 40]))).toBe(true)
  })

  it('three thirds are not complete, the fill button completes them', () => {
    let items = build(['A', 33.33], ['B', 33.33], ['C', 33.33])
    expect(isComplete(items)).toBe(false)
    expect(remainingWeight(items)).toBe(0.01)
    items = fillRemaining(items, 'C')
    expect(isComplete(items)).toBe(true)
    expect(items.find((i) => i.symbol === 'C').weight).toBe(33.34)
  })

  it('fill takes weight off when over 100', () => {
    const items = fillRemaining(build(['A', 70], ['B', 50]), 'B')
    expect(totalWeight(items)).toBe(100)
    expect(items.find((i) => i.symbol === 'B').weight).toBe(30)
  })

  it('weights stay between 0 and 100 and ignore garbage', () => {
    const items = build(['A', 50])
    expect(setWeight(items, 'A', 250)[0].weight).toBe(100)
    expect(setWeight(items, 'A', -5)[0].weight).toBe(0)
    expect(setWeight(items, 'A', NaN)[0].weight).toBe(0)
  })

  it('does not add the same asset twice or more than the maximum', () => {
    const items = build(['A', 10])
    expect(addAsset(items, 'A')).toHaveLength(1)
    let full = []
    for (let i = 0; i < MAX_ASSETS + 3; i++) full = addAsset(full, 'S' + i)
    expect(full).toHaveLength(MAX_ASSETS)
  })

  it('a colour slot is never reused while the asset is still there', () => {
    let items = build(['A', 10], ['B', 10], ['C', 10])
    items = removeAsset(items, 'B')
    const slots = addAsset(items, 'D').map((i) => i.slot)
    expect(new Set(slots).size).toBe(slots.length)
    expect(nextFreeSlot(items)).toBe(1)
  })

  it('builds the API request with fractions that sum to 1', () => {
    const request = toRequestPortfolio(build(['AAPL', 33.33], ['MSFT', 33.33], ['SPY', 33.34]))
    expect(request).toEqual([
      { ticker: 'AAPL', weight: 0.3333 },
      { ticker: 'MSFT', weight: 0.3333 },
      { ticker: 'SPY', weight: 0.3334 },
    ])
    expect(Math.abs(request.reduce((s, r) => s + r.weight, 0) - 1)).toBeLessThan(0.0001)
  })
})
