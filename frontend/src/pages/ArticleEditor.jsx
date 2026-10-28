import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api.js'
import { ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'

function ArticleForm({ article }) {
  const navigate = useNavigate()
  const categories = useLoad(() => api.categories(), [])
  const [form, setForm] = useState({
    title: article ? article.title : '',
    body: article ? article.body : '',
    category_id: article ? String(article.category.id) : '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    const payload = { ...form, category_id: Number(form.category_id) }
    try {
      const saved = article
        ? await api.updateArticle(article.id, payload)
        : await api.createArticle(payload)
      navigate(`/articles/${saved.id}`)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <form className="card narrow" onSubmit={submit}>
      <h1>{article ? 'Edit article' : 'New article'}</h1>
      {!article && <p className="muted">New articles start as drafts. Publish them from the article page.</p>}
      <label>Title</label>
      <input value={form.title} onChange={set('title')} required maxLength={100} />
      <label>Category</label>
      <select value={form.category_id} onChange={set('category_id')} required>
        <option value="">Select a category</option>
        {(categories.data || []).map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <label>Body</label>
      <textarea rows={14} value={form.body} onChange={set('body')} required />
      <ErrorMessage message={error} />
      {busy && article && article.status === 'published' && (
        <p className="muted">Saving a published article re-indexes it, so this can take a moment.</p>
      )}
      <button className="primary" disabled={busy}>
        {busy ? 'Saving…' : 'Save'}
      </button>
    </form>
  )
}

export default function ArticleEditor() {
  const { id } = useParams()
  const article = useLoad(() => (id ? api.article(id) : Promise.resolve(null)), [id])

  if (article.loading) return <Loading />
  if (id && !article.data) return <ErrorMessage message={article.error || 'Article not found'} />
  return <ArticleForm article={article.data} />
}