import { useState } from 'react'
import { api } from '../api.js'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'

export default function Categories() {
  const cats = useLoad(() => api.categories(), [])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState({ name: '', description: '' })
  const [error, setError] = useState('')

  async function run(action) {
    setError('')
    try {
      await action()
      cats.reload()
    } catch (e) {
      setError(e.message)
    }
  }

  const create = (e) => {
    e.preventDefault()
    run(async () => {
      await api.createCategory({ name, description: description || null })
      setName('')
      setDescription('')
    })
  }

  const save = () =>
    run(async () => {
      await api.updateCategory(editingId, {
        name: draft.name,
        description: draft.description || null,
      })
      setEditingId(null)
    })

  const remove = (c) => {
    if (window.confirm(`Delete "${c.name}"?`)) run(() => api.deleteCategory(c.id))
  }

  return (
    <>
      <h1>Categories</h1>
      <form className="card filters" onSubmit={create}>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={50}
        />
        <input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={500}
        />
        <button className="primary">Add category</button>
      </form>

      <ErrorMessage message={error || cats.error} />
      {cats.loading && !cats.data && <Loading />}
      {cats.data && cats.data.length === 0 && <Empty>No categories yet.</Empty>}

      {cats.data && cats.data.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {cats.data.map((c) =>
              editingId === c.id ? (
                <tr key={c.id}>
                  <td>
                    <input
                      value={draft.name}
                      onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                      maxLength={50}
                    />
                  </td>
                  <td>
                    <input
                      value={draft.description}
                      onChange={(e) => setDraft({ ...draft, description: e.target.value })}
                      maxLength={500}
                    />
                  </td>
                  <td className="row">
                    <button className="primary" onClick={save}>
                      Save
                    </button>
                    <button onClick={() => setEditingId(null)}>Cancel</button>
                  </td>
                </tr>
              ) : (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.description || '—'}</td>
                  <td className="row">
                    <button
                      onClick={() => {
                        setEditingId(c.id)
                        setDraft({ name: c.name, description: c.description || '' })
                      }}
                    >
                      Edit
                    </button>
                    <button className="danger" onClick={() => remove(c)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      )}
    </>
  )
}
