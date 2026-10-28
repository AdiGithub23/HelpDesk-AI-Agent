import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'
import { PRIORITIES } from '../utils.js'

export default function NewTicket() {
  const navigate = useNavigate()
  const categories = useLoad(() => api.categories(), [])
  const [form, setForm] = useState({
    title: '',
    description: '',
    category_id: '',
    priority: 'medium',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const ticket = await api.createTicket({ ...form, category_id: Number(form.category_id) })
      navigate(`/tickets/${ticket.id}`)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  if (categories.loading) return <Loading />
  if (categories.data && categories.data.length === 0) {
    return <Empty>There are no categories yet. An agent must create one first.</Empty>
  }

  return (
    <form className="card narrow" onSubmit={submit}>
      <h1>New ticket</h1>
      <label>Title</label>
      <input value={form.title} onChange={set('title')} required maxLength={100} />
      <label>Description</label>
      <textarea rows={6} value={form.description} onChange={set('description')} required />
      <label>Category</label>
      <select value={form.category_id} onChange={set('category_id')} required>
        <option value="">Select a category</option>
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
      <ErrorMessage message={error || categories.error} />
      <button className="primary" disabled={busy}>
        {busy ? 'Creating…' : 'Create ticket'}
      </button>
    </form>
  )
}