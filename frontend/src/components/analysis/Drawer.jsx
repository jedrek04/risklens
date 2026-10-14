import { useEffect, useRef } from 'react'

// a panel that slides in from the right. Escape or the close button closes it.
export default function Drawer({ open, onClose, children }) {
  const closeButton = useRef(null)

  useEffect(() => {
    if (!open) return
    closeButton.current?.focus()
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  return (
    <aside className={open ? 'drawer open' : 'drawer'} role="dialog" aria-label="Details" aria-hidden={!open}>
      <button ref={closeButton} className="btn small close" onClick={onClose} tabIndex={open ? 0 : -1}>Close</button>
      {open && children}
    </aside>
  )
}
