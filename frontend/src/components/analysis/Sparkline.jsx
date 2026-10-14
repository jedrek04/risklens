import { sparkline } from '../../lib/sparkline'

export default function Sparkline({ values, color }) {
  const { path, end } = sparkline(values, 120, 30)
  return (
    <svg viewBox="0 0 120 30" width="120" height="30" aria-hidden="true">
      <path d={path} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={end.x} cy={end.y} r="4" fill={color} stroke="#121722" strokeWidth="2" />
    </svg>
  )
}
