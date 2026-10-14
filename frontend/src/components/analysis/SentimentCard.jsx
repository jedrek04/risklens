import { colorOf } from '../../lib/colors'
import { percent, signed } from '../../lib/format'
import { confidenceRatio, safeUrl, statusInfo } from '../../lib/sentiment'
import { nameOf } from '../../lib/assets'
import Gauge from './Gauge'

function Headline({ item }) {
  const href = safeUrl(item.url)
  return (
    <div>
      {href ? <a href={href} target="_blank" rel="noopener noreferrer">{item.title}</a> : <span>{item.title}</span>}
      <small>
        {item.source}
        <span className={item.score > 0 ? 'badge pos' : 'badge neg'}>{signed(item.score)}</span>
      </small>
    </div>
  )
}

export default function SentimentCard({ asset, slot, needed }) {
  const status = statusInfo(asset.status)
  const low = asset.status === 'low_confidence'
  const share = asset.share
  const headlines = [...(asset.top_positive ?? []).slice(0, 1), ...(asset.top_negative ?? []).slice(0, 1)]

  return (
    <>
      <div className="sc-head">
        <i className="dot" style={{ background: colorOf(slot) }} />
        <b>{asset.ticker}</b>
        <span className="muted name">{nameOf(asset.ticker)}</span>
        <span className={status.good ? 'state ok' : 'state bad'}>{status.text}</span>
      </div>

      <div className="gauge">
        <Gauge score={asset.score} faded={asset.status === 'unavailable'} />
        <div className="gauge-score mono">{asset.score == null ? 'n/a' : signed(asset.score)}</div>
        <div className="gauge-label">{asset.score == null ? '' : `${asset.label} tone`}</div>
      </div>

      <div className={low ? 'conf low' : 'conf'}>
        <div className="conf-text">
          <span>Headlines used</span>
          <span className="mono">{asset.headlines} of {needed} needed</span>
        </div>
        <div className="conf-track"><i style={{ width: `${confidenceRatio(asset.headlines, needed) * 100}%` }} /></div>
      </div>

      {share && (
        <>
          <div className="stack">
            <i style={{ width: `${share.positive * 100}%`, background: '#3987e5' }} />
            <i style={{ width: `${share.neutral * 100}%`, background: '#4a566f' }} />
            <i style={{ width: `${share.negative * 100}%`, background: '#e66767' }} />
          </div>
          <div className="stack-key">
            <span><i style={{ background: '#3987e5' }} />Positive {percent(share.positive, 0)}</span>
            <span><i style={{ background: '#4a566f' }} />Neutral {percent(share.neutral, 0)}</span>
            <span><i style={{ background: '#e66767' }} />Negative {percent(share.negative, 0)}</span>
          </div>
        </>
      )}

      {headlines.length > 0 && <div className="hl">{headlines.map((h) => <Headline key={h.url} item={h} />)}</div>}
      {(low || asset.status === 'unavailable') && asset.message && <p className="note">{asset.message}</p>}
    </>
  )
}
