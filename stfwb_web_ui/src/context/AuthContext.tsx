import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface LinkedIdentity {
  provider: string
  display: string | null
  avatar_url: string | null
  last_login_at: string | null
}

export interface AuthUser {
  user_id: string
  identities: LinkedIdentity[]
}

interface AuthContextType {
  user: AuthUser | null
  userId: string | null
  isLoading: boolean
  error: string | null
  login: () => void
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const API_BASE = 'http://localhost:8000'
  const [user, setUser] = useState<AuthUser | null>(null)
  const [userId, setUserId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUserId = localStorage.getItem('user_id')
    const savedUser = localStorage.getItem('auth_user')

    if (savedUserId && savedUser) {
      try {
        setUserId(savedUserId)
        setUser(JSON.parse(savedUser))
      } catch (err) {
        console.error('Failed to load saved session:', err)
        localStorage.removeItem('user_id')
        localStorage.removeItem('auth_user')
      }
    }

    setIsLoading(false)
  }, [])

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const callbackUserId = params.get('user_id')
    const callbackLogin = params.get('login')
    const callbackError = params.get('error')
    const callbackMessage = params.get('message')

    if (callbackError) {
      setError(callbackMessage || 'Authentication failed')
      window.history.replaceState({}, document.title, window.location.pathname)
    } else if (callbackUserId && callbackLogin) {
      // User ID from OAuth callback (GitHub App flow)
      setUserId(callbackUserId)

      // Fetch full user info from backend
      fetch(`${API_BASE}/auth/user?user_id=${callbackUserId}`)
        .then((res) => res.json())
        .then((data) => {
          setUser(data)
          localStorage.setItem('user_id', callbackUserId)
          localStorage.setItem('auth_user', JSON.stringify(data))
          setError(null)
          // Clean up URL
          window.history.replaceState({}, document.title, window.location.pathname)
        })
        .catch((err) => {
          console.error('Failed to fetch user info:', err)
          setError('Failed to load user information')
        })
    }
  }, [])

  const login = () => {
    // Hit backend directly to avoid frontend dev server path issues
    window.location.href = `${API_BASE}/auth/github/start`
  }

  const logout = async () => {
    if (!userId) return

    try {
      await fetch(`${API_BASE}/auth/logout?user_id=${userId}`, { method: 'POST' })
      setUser(null)
      setUserId(null)
      localStorage.removeItem('user_id')
      localStorage.removeItem('auth_user')
      setError(null)
    } catch (err) {
      console.error('Logout failed:', err)
      setError('Failed to logout')
    }
  }

  return (
    <AuthContext.Provider value={{ user, userId, isLoading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
