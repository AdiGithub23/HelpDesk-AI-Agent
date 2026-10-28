import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth.jsx'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isAgent = user.role === 'agent'

  return (
    <>
      <header className="header">
        <strong className="brand">Helpdesk</strong>
        <nav>
          <NavLink to="/tickets">Tickets</NavLink>
          <NavLink to="/articles">Articles</NavLink>
          <NavLink to="/chat">Assistant</NavLink>
          {isAgent && <NavLink to="/categories">Categories</NavLink>}
          {isAgent && <NavLink to="/users">Users</NavLink>}
        </nav>
        <div className="user">
          <span>
            {user.full_name} <span className="muted">({user.role})</span>
          </span>
          <button
            onClick={() => {
              logout()
              navigate('/login')
            }}
          >
            Log out
          </button>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
