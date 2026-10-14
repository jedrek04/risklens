// a card that shows a loading shimmer, an error with retry, or its content
export default function Card({ title, subtitle, actions, state, wait, onRetry, className = '', children }) {
  const loading = state.status === 'loading' || state.status === 'idle'

  return (
    <section className={`card ${className} ${loading ? 'loading' : ''}`} data-wait={loading ? wait : undefined}>
      {(title || actions) && (
        <div className="card-head">
          {title && <h2>{title}</h2>}
          {subtitle && <span className="sub">{subtitle}</span>}
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      {state.status === 'error' ? (
        <div className="card-error">
          <b>This could not be loaded</b>
          <p>{state.error}</p>
          <button className="btn" onClick={onRetry}>Try again</button>
        </div>
      ) : (
        <div className={state.refreshing ? 'dimmed' : ''}>{loading ? <div className="placeholder" /> : children}</div>
      )}
    </section>
  )
}
