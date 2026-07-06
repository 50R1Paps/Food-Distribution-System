import { beforeEach, describe, expect, it, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('@/api', () => {
  const api = {
    post: vi.fn(),
    get: vi.fn(),
  }
  return { default: api }
})

import api from '@/api'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes with no token when localStorage is empty', () => {
    localStorage.removeItem('access_token')
    const store = useAuthStore()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('initializes with token from localStorage', () => {
    localStorage.setItem('access_token', 'fake-token')
    const store = useAuthStore()
    expect(store.token).toBe('fake-token')
    expect(store.isAuthenticated).toBe(true)
  })

  it('login stores token and fetches user', async () => {
    const mockApi = api as any
    mockApi.post.mockResolvedValue({
      data: { access_token: 'new-token', token_type: 'bearer' },
    })
    mockApi.get.mockResolvedValue({
      data: { id: 1, username: 'admin', created_at: '2024-01-01T00:00:00Z' },
    })

    const store = useAuthStore()
    await store.login('admin', 'password123')

    expect(store.token).toBe('new-token')
    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual({
      id: 1,
      username: 'admin',
      created_at: '2024-01-01T00:00:00Z',
    })
    expect(localStorage.getItem('access_token')).toBe('new-token')
  })

  it('login sends form-urlencoded data', async () => {
    const mockApi = api as any
    mockApi.post.mockResolvedValue({
      data: { access_token: 'tok', token_type: 'bearer' },
    })
    mockApi.get.mockResolvedValue({
      data: { id: 1, username: 'admin', created_at: '2024-01-01T00:00:00Z' },
    })

    const store = useAuthStore()
    await store.login('admin', 'pass')

    expect(mockApi.post).toHaveBeenCalledWith(
      '/auth/login',
      expect.any(URLSearchParams),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
    )
    const params = mockApi.post.mock.calls[0][1] as URLSearchParams
    expect(params.get('username')).toBe('admin')
    expect(params.get('password')).toBe('pass')
  })

  it('logout clears token, user, and localStorage', () => {
    localStorage.setItem('access_token', 'some-token')
    const store = useAuthStore()
    store.user = { id: 1, username: 'admin', created_at: '2024-01-01' }

    store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('fetchUser does nothing when no token', async () => {
    const store = useAuthStore()
    store.token = null
    await store.fetchUser()
    expect(store.user).toBeNull()
  })

  it('fetchUser calls logout on API error', async () => {
    localStorage.setItem('access_token', 'bad-token')
    const mockApi = api as any
    mockApi.get.mockRejectedValue(new Error('401'))

    const store = useAuthStore()
    await store.fetchUser()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})
