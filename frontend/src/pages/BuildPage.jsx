import { useMemo } from 'react'
import AssetSearch from '../components/build/AssetSearch'
import Donut from '../components/build/Donut'
import ModelSettings from '../components/build/ModelSettings'
import PortfolioTable from '../components/build/PortfolioTable'
import TotalBar from '../components/build/TotalBar'
import '../components/build/build.css'
import tickers from '../data/tickers.json'
import { addAsset, isComplete } from '../lib/portfolio'
import { validateSettings } from '../lib/settings'

export default function BuildPage({ items, settings, onItems, onSettings, onCalculate }) {
  const assetsBySymbol = useMemo(() => Object.fromEntries(tickers.map((t) => [t.symbol, t])), [])
  const ready = isComplete(items) && Object.keys(validateSettings(settings)).length === 0

  return (
    <main>
      <div className="eyebrow">Step 1</div>
      <h1>Build your portfolio</h1>
      <p className="lede">
        Search any of the {tickers.length} assets, type a weight for each, and press Calculate. Weights must add up to exactly 100%.
      </p>

      <div className="build-grid">
        <AssetSearch assets={tickers} selected={items.map((i) => i.symbol)} onAdd={(symbol) => onItems(addAsset(items, symbol))} />

        <div className="card">
          <div className="card-head">
            <h2>Your portfolio</h2>
            <span className="sub">
              {items.length} {items.length === 1 ? 'asset' : 'assets'}
            </span>
          </div>
          <div className="donut-wrap">
            <Donut items={items} />
          </div>
          <PortfolioTable items={items} assetsBySymbol={assetsBySymbol} onChange={onItems} />
          <TotalBar items={items} />
          <ModelSettings settings={settings} onChange={onSettings} />
          <div className="cta">
            <button className="btn primary" disabled={!ready} onClick={onCalculate}>
              Calculate
            </button>
            <span className="hint">Risk in about 2 s · news in about 3 s · unusual days in about 20 s</span>
          </div>
        </div>
      </div>
    </main>
  )
}
