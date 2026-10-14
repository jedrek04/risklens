import { factLabel } from '../../lib/report'

const TITLES = { risk: 'Risk', anomalies: 'Unusual days', sentiment: 'News sentiment' }

export default function RawNumbers({ facts }) {
  const groups = {}
  for (const fact of facts) (groups[fact.path[0]] ??= []).push(fact)

  return (
    <div className="card raw">
      <h2>The numbers behind the report</h2>
      <p className="muted small">The same facts the writer received, without any text around them.</p>
      {Object.entries(groups).map(([name, list]) => (
        <div key={name}>
          <h3>{TITLES[name] ?? name}</h3>
          <table>
            <tbody>
              {list.map((fact, i) => (
                <tr key={i}><td>{factLabel(fact.path)}</td><td className="mono">{fact.value}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  )
}
