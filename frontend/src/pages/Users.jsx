import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'

export default function Users() {
  const { user: me } = useAuth()
  const users = useLoad(() => api.users(), [])
  const [error, setError] = useState('')
  const [roles, setRoles] = useState({})
  const [active, setActive] = useState({})

  async function run(action) {
    setError('')
    try {
      await action()
      users.reload()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <h1>Users</h1>
      <ErrorMessage message={error || users.error} />
      {users.loading && !users.data && <Loading />}
      {users.data && users.data.length === 0 && <Empty>No users.</Empty>}

      {!me.is_superior && (
        <p className="muted">Read-only. Only the superior agent can change roles or active status.</p>
      )}

      {users.data && users.data.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {users.data.map((u) => {
              const isMe = u.id === me.id // an agent cannot change their own role or active status
              return (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>
                    {me.is_superior ? (
                      <select
                        value={roles[u.id] ?? u.role}
                        disabled={isMe}
                        title={isMe ? 'You cannot change your own role' : ''}
                        onChange={(e) => {
                          const role = e.target.value
                          setRoles((r) => ({ ...r, [u.id]: role }))
                          run(() => api.setUserRole(u.id, role))
                        }}
                      >
                        <option value="employee">employee</option>
                        <option value="agent">agent</option>
                      </select>
                    ) : (
                      u.role
                    )}
                  </td>
                  <td className="row">
                    <span className={(active[u.id] ?? u.is_active) ? 'ok' : 'muted'}>
                      {(active[u.id] ?? u.is_active) ? 'active' : 'inactive'}
                    </span>
                    {me.is_superior && (
                      <button
                        disabled={isMe}
                        title={isMe ? 'You cannot change your own status' : ''}
                        onClick={() => {
                          const next = !(active[u.id] ?? u.is_active)
                          setActive((a) => ({ ...a, [u.id]: next }))
                          run(() => api.setUserActive(u.id, next))
                        }}
                      >
                        {(active[u.id] ?? u.is_active) ? 'Deactivate' : 'Activate'}
                      </button>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </>
  )
}
