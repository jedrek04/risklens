import { MAX_ASSETS } from '../config'

// a portfolio is a list of { symbol, weight, slot }. weight is in percent, slot picks the colour.
const round2 = (x) => Math.round(x * 100) / 100
const clamp = (x) => Math.min(100, Math.max(0, Number.isFinite(x) ? x : 0))

export const totalWeight = (items) => round2(items.reduce((sum, item) => sum + item.weight, 0))

export const remainingWeight = (items) => round2(100 - totalWeight(items))

export const isComplete = (items) => items.length > 0 && Math.abs(remainingWeight(items)) < 0.005

export function nextFreeSlot(items) {
  const used = new Set(items.map((item) => item.slot))
  for (let slot = 0; slot < MAX_ASSETS; slot++) {
    if (!used.has(slot)) return slot
  }
  return -1
}

export function addAsset(items, symbol) {
  if (items.length >= MAX_ASSETS || items.some((item) => item.symbol === symbol)) return items
  const weight = clamp(remainingWeight(items))
  return [...items, { symbol, weight, slot: nextFreeSlot(items) }]
}

export const removeAsset = (items, symbol) => items.filter((item) => item.symbol !== symbol)

export const setWeight = (items, symbol, weight) =>
  items.map((item) => (item.symbol === symbol ? { ...item, weight: clamp(round2(weight)) } : item))

export function fillRemaining(items, symbol) {
  const remaining = remainingWeight(items)
  return items.map((item) =>
    item.symbol === symbol ? { ...item, weight: clamp(round2(item.weight + remaining)) } : item,
  )
}

// the API wants fractions that sum to 1, not percent
export const toRequestPortfolio = (items) =>
  items.map((item) => ({ ticker: item.symbol, weight: Math.round(item.weight * 100) / 10000 }))
