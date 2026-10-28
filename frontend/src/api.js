const BASE = '/api/v1'
const TOKEN_KEY = 'helpdesk_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

let onUnauthorized = () => {}
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn
}

// Our own errors return detail as a string; validation errors (422) return a list.
function errorMessage(body, status) {
  const detail = body && body.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc.filter((p) => p !== 'body').join('.') : ''
        return field ? `${field}: ${d.msg}` : d.msg
      })
      .join('; ')
  }
  return `Request failed (${status})`
}

async function request(path, { method = 'GET', json, form, params } = {}) {
  let url = BASE + path
  if (params) {
    const qs = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') qs.append(key, value)
    }
    const text = qs.toString()
    if (text) url += '?' + text
  }

  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let body
  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  } else if (form) {
    body = new URLSearchParams(form) // the browser sets the form content type
  }

  let res
  try {
    res = await fetch(url, { method, headers, body })
  } catch {
    throw new Error('Cannot reach the server. Is the backend running?')
  }

  if (res.status === 204) return null

  let data = null
  try {
    data = await res.json()
  } catch {
    // empty or non-JSON body
  }

  if (!res.ok) {
    if (res.status === 401 && token) {
      clearToken()
      onUnauthorized()
    }
    const err = new Error(errorMessage(data, res.status))
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  // auth and users
  login: (email, password) =>
    request('/auth/login', { method: 'POST', form: { username: email, password } }),
  register: (data) => request('/auth/register', { method: 'POST', json: data }),
  me: () => request('/users/me'),
  users: (role) => request('/users', { params: { role } }),
  setUserRole: (id, role) => request(`/users/${id}/role`, { method: 'PATCH', json: { role } }),
  setUserActive: (id, is_active) =>
    request(`/users/${id}/active`, { method: 'PATCH', json: { is_active } }),

  // categories
  categories: () => request('/categories'),
  createCategory: (data) => request('/categories', { method: 'POST', json: data }),
  updateCategory: (id, data) => request(`/categories/${id}`, { method: 'PATCH', json: data }),
  deleteCategory: (id) => request(`/categories/${id}`, { method: 'DELETE' }),

  // tickets and comments
  tickets: (params) => request('/tickets', { params }),
  ticket: (id) => request(`/tickets/${id}`),
  createTicket: (data) => request('/tickets', { method: 'POST', json: data }),
  updateTicket: (id, data) => request(`/tickets/${id}`, { method: 'PATCH', json: data }),
  setTicketStatus: (id, status) =>
    request(`/tickets/${id}/status`, { method: 'PATCH', json: { status } }),
  assignTicket: (id, assignee_id) =>
    request(`/tickets/${id}/assignee`, { method: 'PUT', json: { assignee_id } }),
  comments: (ticketId) => request(`/tickets/${ticketId}/comments`),
  addComment: (ticketId, data) =>
    request(`/tickets/${ticketId}/comments`, { method: 'POST', json: data }),

  // articles
  articles: (params) => request('/articles', { params }),
  article: (id) => request(`/articles/${id}`),
  createArticle: (data) => request('/articles', { method: 'POST', json: data }),
  updateArticle: (id, data) => request(`/articles/${id}`, { method: 'PATCH', json: data }),
  setArticleStatus: (id, status) =>
    request(`/articles/${id}/status`, { method: 'PATCH', json: { status } }),
  deleteArticle: (id) => request(`/articles/${id}`, { method: 'DELETE' }),

  // chat
  chatSessions: (params) => request('/chat/sessions', { params }),
  createChat: () => request('/chat/sessions', { method: 'POST' }),
  chatMessages: (id) => request(`/chat/sessions/${id}/messages`),
  ask: (id, content) =>
    request(`/chat/sessions/${id}/messages`, { method: 'POST', json: { content } }),

  // triage
  triageRuns: (ticketId) => request(`/tickets/${ticketId}/triage-runs`),
  startTriage: (ticketId) => request(`/tickets/${ticketId}/triage-runs`, { method: 'POST' }),
  decideTriage: (runId, data) =>
    request(`/triage-runs/${runId}/decision`, { method: 'POST', json: data }),
}