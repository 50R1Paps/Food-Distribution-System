import { beforeEach, describe, expect, it, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('@/api', () => {
  const api = {
    post: vi.fn(),
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return { default: api }
})

import router from '@/router'
import { useAuthStore } from '@/stores/auth'

describe('Router guards', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('redirects to login when not authenticated', async () => {
    const auth = useAuthStore()
    auth.token = null

    await router.push('/families')
    await router.isReady()

    expect(router.currentRoute.value.name).toBe('login')
  })

  it('allows access to public routes when not authenticated', async () => {
    const auth = useAuthStore()
    auth.token = null

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.name).toBe('login')
  })

  it('allows access to protected routes when authenticated', async () => {
    const auth = useAuthStore()
    auth.token = 'valid-token'

    await router.push('/families')
    await router.isReady()

    expect(router.currentRoute.value.name).toBe('families')
  })

  it('redirects authenticated users away from login page', async () => {
    const auth = useAuthStore()
    auth.token = 'valid-token'

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.name).toBe('home')
  })
})
