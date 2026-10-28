import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import Badge from '../components/Badge.jsx'
import { ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'
import { fmt } from '../utils.js'

export default function ArticleDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAgent = user.role === 'agent'
  const article = useLoad(() => api.article(id), [id])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  if (article.loading && !article.data) return <Loading />
  if (!article.data) return <ErrorMessage message={article.error || 'Article not found'} />

  const a = article.data
  const published = a.status === 'published'

  async function toggleStatus() {
    setBusy(true)
    setError('')
    try {
      await api.setArticleStatus(a.id, published ? 'draft' : 'published')
      article.reload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function remove() {
    if (!window.confirm('Delete this article?')) return
    setBusy(true)
    setError('')
    try {
      await api.deleteArticle(a.id)
      navigate('/articles')
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <div className="page-head">
        <h1>{a.title}</h1>
        {isAgent && <Badge value={a.status} />}
      </div>
      <p className="muted">
        {a.category.name} · by {a.author.full_name} · updated {fmt(a.updated_at)}
      </p>
      <div className="prewrap prose">{a.body}</div>

      {isAgent && (
        <div className="row">
          <Link to={`/articles/${a.id}/edit`} className="button">
            Edit
          </Link>
          <button disabled={busy} onClick={toggleStatus}>
            {busy ? 'Working…' : published ? 'Unpublish' : 'Publish'}
          </button>
          <button className="danger" disabled={busy} onClick={remove}>
            Delete
          </button>
        </div>
      )}
      <ErrorMessage message={error} />
      <p>
        <Link to="/articles">← Back to articles</Link>
      </p>
    </section>
  )
}



