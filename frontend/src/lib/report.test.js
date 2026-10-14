import { describe, expect, it } from 'vitest'
import { annotate, factIndex, factLabel, flattenFacts, reportTexts, verifiedCount } from './report'

const facts = flattenFacts({
  risk: { var: '5.0%', horizon_days: 10, assets: [{ ticker: 'AAPL', weight: '30%' }] },
  anomalies: { portfolio: { latest_date: '2026-10-09' } },
})

describe('facts', () => {
  it('flattens nested objects and lists into paths and text values', () => {
    expect(facts.map((f) => f.path.join('.'))).toEqual([
      'risk.var', 'risk.horizon_days', 'risk.assets.0.ticker', 'risk.assets.0.weight', 'anomalies.portfolio.latest_date',
    ])
    expect(facts[1].value).toBe('10')
  })

  it('labels a fact for a person', () => {
    expect(factLabel(['risk', 'var'])).toBe('risk · Value at Risk')
    expect(factLabel(['risk', 'assets', '0', 'weight'])).toBe('assets · Weight')
    expect(factLabel(['risk', 'some_new_field'])).toBe('risk · some new field')
  })
})

describe('annotating a text', () => {
  const index = factIndex(facts)

  it('keeps the original text when the pieces are joined', () => {
    const text = 'Over a 10-day horizon the loss is 5.0% and 99 other things.'
    expect(annotate(text, index).map((p) => p.text).join('')).toBe(text)
  })

  it('links numbers to the facts that contain them and leaves unknown numbers unlinked', () => {
    const parts = annotate('VaR is 5.0% over 10 days, not 77%.', index).filter((p) => p.isNumber)
    expect(parts.map((p) => [p.text, p.fact !== null])).toEqual([['5.0', true], ['10', true], ['77', false]])
  })

  it('compares numbers by value, like the backend: 9 matches 09 and 5 matches 5.0', () => {
    expect(annotate('on 9 October 2026', index).filter((p) => p.fact !== null).map((p) => p.text)).toEqual(['9', '2026'])
    expect(annotate('a loss of 5 percent', index).find((p) => p.isNumber).fact).not.toBeNull()
  })

  it('counts numbers and verified numbers over several texts', () => {
    expect(verifiedCount(['5.0% of 30%', 'and 123'], index)).toEqual({ numbers: 3, verified: 2 })
  })

  it('collects every text of a report', () => {
    const report = { title: 'T', sections: [{ heading: 'A', body: 'b1' }, { heading: 'B', body: 'b2', bullets: ['x', 'y'] }] }
    expect(reportTexts(report)).toEqual(['T', 'b1', 'b2', 'x', 'y'])
  })
})
