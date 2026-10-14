export default function InfoTip({ text }) {
  return (
    <span className="info" tabIndex={0} data-tip={text} aria-label={text}>
      i
    </span>
  )
}
