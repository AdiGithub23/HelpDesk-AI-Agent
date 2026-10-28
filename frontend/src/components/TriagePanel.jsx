import { useState } from 'react'
import { api } from '../api.js'
import { useLoad } from '../hooks.js'
import { fmt } from '../utils.js'
import Badge from './Badge.jsx'
import { ErrorMessage, Loading } from './Feedback.jsx'

function ReviewForm({ run, onDecided }) {
  const [text, setText] = useState(run.draft_reply || '')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function decide(action) {
    setBusy(true)
    setError('')
    try {
      await api.decideTriage(run.id, { action, text: action === 'edit' ? text : null })
      onDecided(action)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <label>Draft reply (you can edit it before sending)</label>
      <textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} />
      <div className="row">
        <button className="primary" disabled={busy} onClick={() => decide('approve')}>
          Approve draft as it is
        </button>
        <button disabled={busy || !text.trim()} onClick={() => decide('edit')}>
          Send edited text
        </button>
        <button className="danger" disabled={busy} onClick={() => decide('reject')}>
          Reject
        </button>
      </div>
      {busy && <p className="muted">Working…</p>}
      <ErrorMessage message={error} />
    </div>
  )
}

export default function TriagePanel({ ticketId, onSent }) {
  const runs = useLoad(() => api.triageRuns(ticketId), [ticketId])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const list = runs.data || []
  const active = list.find((r) => r.status === 'running' || r.status === 'awaiting_review')

  async function start() {
    setBusy(true)
    setError('')
    try {
      await api.startTriage(ticketId)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
      runs.reload()
    }
  }

  function decided(action) {
    runs.reload()
    if (action !== 'reject') onSent() // a public comment was posted: refresh the comments
  }

  return (
    <section className="card">
      <div className="page-head">
        <h2>AI triage</h2>
        <button className="primary" disabled={busy || Boolean(active)} onClick={start}>
          {busy ? 'Working…' : 'Start AI triage'}
        </button>
      </div>
      {busy && <p className="muted">The AI is reading the ticket. This takes a few seconds.</p>}
      <ErrorMessage message={error} />
      {runs.loading && !runs.data && <Loading />}
      <ErrorMessage message={runs.error} />
      {active && !busy && active.status === 'running' && (
        <p className="muted">A run is marked as running, so a new one cannot be started.</p>
      )}

      {list.map((r) => (
        <div className="run" key={r.id}>
          <div className="row">
            <strong>Run #{r.id}</strong>
            <Badge value={r.status} />
            <span className="muted">{fmt(r.created_at)}</span>
          </div>
          {r.summary && (
            <p>
              <b>Summary:</b> {r.summary}
            </p>
          )}
          {r.suggested_priority && (
            <p>
              <b>Suggested priority:</b> <Badge value={r.suggested_priority} />
            </p>
          )}
          {r.sources && r.sources.length > 0 && (
            <p>
              <b>Based on:</b> {r.sources.map((s) => `${s.title} (#${s.article_id})`).join(', ')}
            </p>
          )}
          {r.status === 'awaiting_review' && <ReviewForm run={r} onDecided={decided} />}
          {r.status === 'sent' && (
            <p className="prewrap">
              <b>Sent reply:</b> {r.final_reply}
            </p>
          )}
          {r.status === 'handed_off' && (
            <p className="muted">
              The knowledge base does not answer this ticket. Handle it manually.
            </p>
          )}
          {r.status === 'rejected' && <p className="muted">The draft was rejected.</p>}
          {r.status === 'failed' && <ErrorMessage message={r.error || 'The run failed.'} />}
        </div>
      ))}
    </section>
  )
}

