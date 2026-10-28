import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import Badge from '../components/Badge.jsx'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import Pagination from '../components/Pagination.jsx'
import { useLoad } from '../hooks.js'
import { fmt } from '../utils.js'

const LIMIT = 20

export default function Articles() {
  const { user } = useAuth()
  const isAgent = user.role === 'agent'
  const [categoryId, setCategoryId] = useState('')
  const [status, setStatus] = useState('')
  const [offset, setOffset] = useState(0)

  const categories = useLoad(() => api.categories(), [])
  const articles = useLoad(
    () => api.articles({ category_id: categoryId, status, limit: LIMIT, offset }),
    [categoryId, status, offset],
  )

  const change = (setter) => (e) => {
    setter(e.target.value)
    setOffset(0)
  }
  const rows = articles.data || []

  return (
    <>
      <div className="page-head">
        <h1>Knowledge base</h1>
        {isAgent && (
          <Link to="/articles/new" className="button primary">
            New article
          </Link>
        )}
      </div>

      <div className="filters">
        <select value={categoryId} onChange={change(setCategoryId)}>
          <option value="">All categories</option>
          {(categories.data || []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {isAgent && (
          <select value={status} onChange={change(setStatus)}>
            <option value="">All statuses</option>
            <option value="draft">draft</option>
            <option value="published">published</option>
          </select>
        )}
      </div>

      <ErrorMessage message={articles.error} />
      {articles.loading && !articles.data && <Loading />}
      {articles.data && rows.length === 0 && (
        <Empty>{offset > 0 ? 'No more articles.' : 'No articles found.'}</Empty>
      )}

      {rows.map((a) => (
        <div className="card" key={a.id}>
          <div className="row">
            <Link to={`/articles/${a.id}`}>
              <strong>{a.title}</strong>
            </Link>
            {isAgent && <Badge value={a.status} />}
          </div>
          <p className="muted">
            {a.category.name} · by {a.author.full_name} · updated {fmt(a.updated_at)}
          </p>
        </div>
      ))}

      {(rows.length > 0 || offset > 0) && (
        <Pagination offset={offset} limit={LIMIT} count={rows.length} onChange={setOffset} />
      )}
    </>
  )
}



