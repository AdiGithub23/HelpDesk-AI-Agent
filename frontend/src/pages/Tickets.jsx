import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import Badge from '../components/Badge.jsx'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import Pagination from '../components/Pagination.jsx'
import { useLoad } from '../hooks.js'
import { STATUSES, fmt, pretty } from '../utils.js'

const LIMIT = 20

export default function Tickets() {
  const { user } = useAuth()
  const isAgent = user.role === 'agent'
  const [status, setStatus] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [assignedTo, setAssignedTo] = useState('')
  const [offset, setOffset] = useState(0)

  const categories = useLoad(() => api.categories(), [])
  const agents = useLoad(() => (isAgent ? api.users('agent') : Promise.resolve([])), [isAgent])
  const tickets = useLoad(
    () =>
      api.tickets({
        status,
        category_id: categoryId,
        assigned_to: assignedTo,
        limit: LIMIT,
        offset,
      }),
    [status, categoryId, assignedTo, offset],
  )

  const change = (setter) => (e) => {
    setter(e.target.value)
    setOffset(0)
  }
  const rows = tickets.data || []

  return (
    <>
      <div className="page-head">
        <h1>{isAgent ? 'All tickets' : 'My tickets'}</h1>
        <Link to="/tickets/new" className="button primary">
          New ticket
        </Link>
      </div>

      <div className="filters">
        <select value={status} onChange={change(setStatus)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {pretty(s)}
            </option>
          ))}
        </select>
        <select value={categoryId} onChange={change(setCategoryId)}>
          <option value="">All categories</option>
          {(categories.data || []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {isAgent && (
          <select value={assignedTo} onChange={change(setAssignedTo)}>
            <option value="">Any assignee</option>
            {(agents.data || []).map((a) => (
              <option key={a.id} value={a.id}>
                {a.full_name}
              </option>
            ))}
          </select>
        )}
      </div>

      <ErrorMessage message={tickets.error} />
      {tickets.loading && !tickets.data && <Loading />}
      {tickets.data && rows.length === 0 && (
        <Empty>{offset > 0 ? 'No more tickets.' : 'No tickets found.'}</Empty>
      )}

      {rows.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              {isAgent && <th>Requester</th>}
              <th>Category</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Assignee</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>
                  <Link to={`/tickets/${t.id}`}>{t.title}</Link>
                </td>
                {isAgent && <td>{t.creator.full_name}</td>}
                <td>{t.category.name}</td>
                <td>
                  <Badge value={t.priority} />
                </td>
                <td>
                  <Badge value={t.status} />
                </td>
                <td>{t.assignee ? t.assignee.full_name : '—'}</td>
                <td>{fmt(t.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {(rows.length > 0 || offset > 0) && (
        <Pagination offset={offset} limit={LIMIT} count={rows.length} onChange={setOffset} />
      )}
    </>
  )
}


