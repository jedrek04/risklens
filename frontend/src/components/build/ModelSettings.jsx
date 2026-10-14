import { LIMITS } from '../../config'
import { validateSettings } from '../../lib/settings'

export default function ModelSettings({ settings, onChange }) {
  const errors = validateSettings(settings)

  return (
    <details className="settings" style={{ marginTop: 14 }}>
      <summary>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m4 2 4 4-4 4" />
        </svg>
        Model settings
      </summary>
      <div className="fields">
        {Object.entries(LIMITS).map(([key, { min, max, label }]) => (
          <div key={key} className={errors[key] ? 'field err' : 'field'}>
            <label htmlFor={`setting-${key}`}>{label}</label>
            <div className="num-input">
              <input
                id={`setting-${key}`}
                type="number"
                min={min}
                max={max}
                value={Number.isNaN(settings[key]) ? '' : settings[key]}
                onChange={(e) => onChange({ ...settings, [key]: e.target.value === '' ? NaN : Number(e.target.value) })}
              />
            </div>
            <small>{`${min.toLocaleString('en-US')} to ${max.toLocaleString('en-US')}`}</small>
          </div>
        ))}
      </div>
    </details>
  )
}
