import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { Empty, ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'

export default function Users() {
  const { user: me } = useAuth()
  const users = useLoad(() => api.users(), [])
  const [error, setError] = useState('')

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
                    <select
                      value={u.role}
                      disabled={isMe}
                      title={isMe ? 'You cannot change your own role' : ''}
                      onChange={(e) => run(() => api.setUserRole(u.id, e.target.value))}
                    >
                      <option value="employee">employee</option>
                      <option value="agent">agent</option>
                    </select>
                  </td>
                  <td className="row">
                    <span className={u.is_active ? 'ok' : 'muted'}>{u.is_active ? 'active' : 'inactive'}</span>
                    <button
                      disabled={isMe}
                      title={isMe ? 'You cannot change your own status' : ''}
                      onClick={() => run(() => api.setUserActive(u.id, !u.is_active))}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
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

