import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { ErrorMessage } from '../components/Feedback.jsx'

export default function Register() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', full_name: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/tickets" replace />

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.register(form)
      await login(form.email, form.password) // register returns no token, so sign in
      navigate('/tickets')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <h1>Create an account</h1>
        <label>Full name</label>
        <input value={form.full_name} onChange={set('full_name')} required maxLength={100} />
        <label>Email</label>
        <input type="email" value={form.email} onChange={set('email')} required />
        <label>Password (at least 8 characters)</label>
        <input
          type="password"
          value={form.password}
          onChange={set('password')}
          required
          minLength={8}
          maxLength={128}
        />
        <ErrorMessage message={error} />
        <button className="primary" disabled={busy}>
          {busy ? 'Creating…' : 'Register'}
        </button>
        <p className="muted">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  )
}