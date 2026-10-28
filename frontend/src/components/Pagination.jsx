export default function Pagination({ offset, limit, count, onChange }) {
  return (
    <div className="pagination">
      <button disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>
        ← Previous
      </button>
      <span className="muted">Page {offset / limit + 1}</span>
      <button disabled={count < limit} onClick={() => onChange(offset + limit)}>
        Next →
      </button>
    </div>
  )
}

