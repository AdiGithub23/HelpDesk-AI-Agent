import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, clearToken, getToken, setToken, setUnauthorizedHandler } from './api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getToken()))

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(logout) // any 401 logs the user out
    if (!getToken()) return
    api
      .me()
      .then(setUser)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [logout])

  async function login(email, password) {
    const { access_token } = await api.login(email, password)
    setToken(access_token)
    setUser(await api.me())
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}