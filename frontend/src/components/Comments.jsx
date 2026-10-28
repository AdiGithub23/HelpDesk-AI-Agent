import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { useLoad } from '../hooks.js'
import { fmt } from '../utils.js'
import Badge from './Badge.jsx'
import { Empty, ErrorMessage, Loading } from './Feedback.jsx'

export default function Comments({ ticketId, reloadKey }) {
  const { user } = useAuth()
  const isAgent = user.role === 'agent'
  const comments = useLoad(() => api.comments(ticketId), [ticketId, reloadKey])
  const [body, setBody] = useState('')
  const [internal, setInternal] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.addComment(ticketId, { body, is_internal: isAgent && internal })
      setBody('')
      setInternal(false)
      comments.reload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <h2>Comments</h2>
      {comments.loading && !comments.data && <Loading />}
      <ErrorMessage message={comments.error} />
      {comments.data && comments.data.length === 0 && <Empty>No comments yet.</Empty>}
      {(comments.data || []).map((c) => (
        <div key={c.id} className={`comment ${c.is_internal ? 'comment-internal' : ''}`}>
          <div className="row">
            <strong>{c.author.full_name}</strong>
            <Badge value={c.author.role} />
            {c.is_internal && <Badge value="internal" />}
            <span className="muted">{fmt(c.created_at)}</span>
          </div>
          <p className="prewrap">{c.body}</p>
        </div>
      ))}

      <form onSubmit={submit}>
        <label>Add a comment</label>
        <textarea rows={3} value={body} onChange={(e) => setBody(e.target.value)} required />
        {isAgent && (
          <label className="checkbox">
            <input
              type="checkbox"
              checked={internal}
              onChange={(e) => setInternal(e.target.checked)}
            />
            Internal note (hidden from the employee)
          </label>
        )}
        <ErrorMessage message={error} />
        <button className="primary" disabled={busy || !body.trim()}>
          {busy ? 'Sending…' : 'Add comment'}
        </button>
      </form>
    </section>
  )
}


