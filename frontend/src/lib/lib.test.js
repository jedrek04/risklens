import { describe, expect, it } from 'vitest'
import { friendlyError } from '../api'
import { niceTicks, tickDecimals } from './chart'
import { percent, seconds, signed } from './format'
import { riskShares } from './riskShare'

describe('format', () => {
  it('writes percents with a real minus sign and optional plus', () => {
    expect(percent(0.0496)).toBe('5.0%')
    expect(percent(-0.0496)).toBe('−5.0%')
    expect(percent(0.053, 1, { sign: true })).toBe('+5.3%')
    expect(percent(0.4382, 0)).toBe('44%')
  })

  it('never shows a minus or plus on a zero', () => {
    expect(percent(-0.00001)).toBe('0.0%')
    expect(percent(0.00001, 1, { sign: true })).toBe('0.0%')
    expect(signed(-0.001)).toBe('0.00')
  })

  it('writes signed scores and seconds', () => {
    expect(signed(0.287)).toBe('+0.29')
    expect(signed(-0.22)).toBe('−0.22')
    expect(seconds(2.14)).toBe('2.1 s')
  })
})

describe('chart ticks', () => {
  it('gives round values that include zero when the range crosses it', () => {
    const ticks = niceTicks(-0.06, 0.06)
    expect(ticks).toContain(0)
    expect(ticks.every((t) => t >= -0.06 && t <= 0.06)).toBe(true)
  })

  it('uses a decimal on the axis when the step is 2.5 percent', () => {
    expect(tickDecimals(niceTicks(-0.055, 0.055))).toBe(1)
    expect(tickDecimals(niceTicks(-0.3, 0.3))).toBe(0)
  })
})

describe('risk shares', () => {
  const asset = (ticker, weight, vol) => ({ ticker, weight, annualized_vol: vol })

  it('shares add up to 100 percent', () => {
    const risk = {
      assets: [asset('A', 0.5, 0.2), asset('B', 0.3, 0.4), asset('C', 0.2, 0.1)],
      correlation: { tickers: ['A', 'B', 'C'], matrix: [[1, 0.3, 0.1], [0.3, 1, 0.5], [0.1, 0.5, 1]] },
    }
    expect(riskShares(risk).reduce((s, r) => s + r.share, 0)).toBeCloseTo(1, 10)
  })

  it('a single asset brings all of the risk', () => {
    const risk = { assets: [asset('A', 1, 0.3)], correlation: { tickers: ['A'], matrix: [[1]] } }
    expect(riskShares(risk)[0].share).toBeCloseTo(1, 10)
  })

  it('equal uncorrelated assets share the risk equally', () => {
    const risk = {
      assets: [asset('A', 0.5, 0.2), asset('B', 0.5, 0.2)],
      correlation: { tickers: ['A', 'B'], matrix: [[1, 0], [0, 1]] },
    }
    const [a, b] = riskShares(risk)
    expect(a.share).toBeCloseTo(0.5, 10)
    expect(b.share).toBeCloseTo(0.5, 10)
  })

  it('a more volatile asset with the same weight brings more of the risk', () => {
    const risk = {
      assets: [asset('CALM', 0.5, 0.1), asset('WILD', 0.5, 0.5)],
      correlation: { tickers: ['CALM', 'WILD'], matrix: [[1, 0.2], [0.2, 1]] },
    }
    const [calm, wild] = riskShares(risk)
    expect(wild.share).toBeGreaterThan(calm.share)
  })
})

describe('api errors', () => {
  it('shows the server message for data problems and a plain message otherwise', () => {
    expect(friendlyError(400, { detail: 'No data for ticker(s): ZZZ' })).toBe('No data for ticker(s): ZZZ')
    expect(friendlyError(422, { detail: [] })).toMatch(/not valid/)
    expect(friendlyError(502, null)).toMatch(/try again/i)
    expect(friendlyError(500, { detail: 'secret internal detail' })).not.toMatch(/secret/)
  })
})
