import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { Loading } from './Feedback.jsx'

export default function ProtectedRoute({ agentOnly = false }) {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  if (agentOnly && user.role !== 'agent') return <Navigate to="/tickets" replace />
  return <Outlet />
}



