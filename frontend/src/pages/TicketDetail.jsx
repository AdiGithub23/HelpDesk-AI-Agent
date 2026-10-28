import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import Badge from '../components/Badge.jsx'
import Comments from '../components/Comments.jsx'
import { ErrorMessage, Loading } from '../components/Feedback.jsx'
import TriagePanel from '../components/TriagePanel.jsx'
import { useLoad } from '../hooks.js'
import { PRIORITIES, allowedStatuses, fmt, statusActionLabel } from '../utils.js'

function EditForm({ ticket, onDone }) {
  const categories = useLoad(() => api.categories(), [])
  const [form, setForm] = useState({
    title: ticket.title,
    description: ticket.description,
    category_id: String(ticket.category.id),
    priority: ticket.priority,
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.updateTicket(ticket.id, { ...form, category_id: Number(form.category_id) })
      onDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit}>
      <label>Title</label>
      <input value={form.title} onChange={set('title')} required maxLength={100} />
      <label>Description</label>
      <textarea rows={5} value={form.description} onChange={set('description')} required />
      <label>Category</label>
      <select value={form.category_id} onChange={set('category_id')}>
        {(categories.data || []).map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <label>Priority</label>
      <select value={form.priority} onChange={set('priority')}>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <ErrorMessage message={error} />
      <div className="row">
        <button className="primary" disabled={busy}>
          {busy ? 'Saving…' : 'Save'}
        </button>
        <button type="button" onClick={() => onDone(false)}>
          Cancel
        </button>
      </div>
    </form>
  )
}

function AssignForm({ ticket, onDone }) {
  const agents = useLoad(() => api.users('agent'), [])
  const active = (agents.data || []).filter((a) => a.is_active) // a deactivated agent is refused (rule 12)
  const [assignee, setAssignee] = useState(ticket.assignee ? String(ticket.assignee.id) : '')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function assign() {
    setBusy(true)
    setError('')
    try {
      await api.assignTicket(ticket.id, Number(assignee))
      onDone()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <label>Assign to</label>
      <div className="row">
        <select value={assignee} onChange={(e) => setAssignee(e.target.value)}>
          <option value="">Select an agent</option>
          {active.map((a) => (
            <option key={a.id} value={a.id}>
              {a.full_name}
            </option>
          ))}
        </select>
        <button disabled={!assignee || busy} onClick={assign}>
          Assign
        </button>
      </div>
      <ErrorMessage message={error} />
    </div>
  )
}

export default function TicketDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const isAgent = user.role === 'agent'
  const ticket = useLoad(() => api.ticket(id), [id])
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [commentsKey, setCommentsKey] = useState(0)

  if (ticket.loading && !ticket.data) return <Loading />
  if (!ticket.data) return <ErrorMessage message={ticket.error || 'Ticket not found'} />

  const t = ticket.data
  const canEdit = isAgent || t.status === 'open' // employees can edit only while open
  const nextStatuses = allowedStatuses(t.status, user.role)

  async function changeStatus(status) {
    setBusy(true)
    setError('')
    try {
      await api.setTicketStatus(t.id, status)
      ticket.reload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <section className="card">
        {editing ? (
          <EditForm
            ticket={t}
            onDone={(saved) => {
              setEditing(false)
              if (saved) ticket.reload()
            }}
          />
        ) : (
          <>
            <div className="page-head">
              <h1>
                #{t.id} {t.title}
              </h1>
              {canEdit && <button onClick={() => setEditing(true)}>Edit</button>}
            </div>
            <div className="row">
              <Badge value={t.status} />
              <Badge value={t.priority} />
            </div>
            <p className="meta">
              Category: <b>{t.category.name}</b> · Requester: <b>{t.creator.full_name}</b> ·
              Assignee: <b>{t.assignee ? t.assignee.full_name : 'none'}</b>
              <br />
              Created {fmt(t.created_at)} · Updated {fmt(t.updated_at)}
            </p>
            <p className="prewrap">{t.description}</p>
          </>
        )}
      </section>

      {(nextStatuses.length > 0 || isAgent) && (
        <section className="card">
          <h2>Actions</h2>
          {nextStatuses.length > 0 && (
            <div className="row">
              {nextStatuses.map((s) => (
                <button key={s} disabled={busy} onClick={() => changeStatus(s)}>
                  {statusActionLabel(t.status, s)}
                </button>
              ))}
            </div>
          )}
          {isAgent && <AssignForm ticket={t} onDone={ticket.reload} />}
          <ErrorMessage message={error} />
        </section>
      )}

      {isAgent && (
        <TriagePanel ticketId={t.id} onSent={() => setCommentsKey((k) => k + 1)} />
      )}
      <Comments ticketId={t.id} reloadKey={commentsKey} />
    </>
  )
}



