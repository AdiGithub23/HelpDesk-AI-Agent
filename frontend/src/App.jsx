import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import ArticleDetail from './pages/ArticleDetail.jsx'
import ArticleEditor from './pages/ArticleEditor.jsx'
import Articles from './pages/Articles.jsx'
import Categories from './pages/Categories.jsx'
import Chat from './pages/Chat.jsx'
import Login from './pages/Login.jsx'
import NewTicket from './pages/NewTicket.jsx'
import Register from './pages/Register.jsx'
import TicketDetail from './pages/TicketDetail.jsx'
import Tickets from './pages/Tickets.jsx'
import Users from './pages/Users.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/tickets" replace />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/tickets/new" element={<NewTicket />} />
          <Route path="/tickets/:id" element={<TicketDetail />} />
          <Route path="/articles" element={<Articles />} />
          <Route path="/articles/:id" element={<ArticleDetail />} />
          <Route path="/chat" element={<Chat />} />

          <Route element={<ProtectedRoute agentOnly />}>
            <Route path="/articles/new" element={<ArticleEditor />} />
            <Route path="/articles/:id/edit" element={<ArticleEditor />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/users" element={<Users />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/tickets" replace />} />
    </Routes>
  )
}
