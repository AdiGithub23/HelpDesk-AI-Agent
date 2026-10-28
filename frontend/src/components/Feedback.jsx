export function Loading() {
  return <p className="muted">Loading…</p>
}

export function ErrorMessage({ message }) {
  return message ? <p className="error">{message}</p> : null
}

export function Empty({ children }) {
  return <p className="muted">{children}</p>
}



