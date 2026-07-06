import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'

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

import api from '@/api'
import LoginView from '@/views/LoginView.vue'

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    ],
  })
}

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('renders form with username and password fields', () => {
    const router = makeRouter()
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.find('#username').exists()).toBe(true)
    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toContain('Accedi')
  })

  it('shows error message on login failure', async () => {
    const mockApi = api as any
    mockApi.post.mockRejectedValue({
      response: { data: { detail: 'Username o password errati' } },
    })

    const router = makeRouter()
    await router.push('/login')
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('#username').setValue('wrong')
    await wrapper.find('#password').setValue('creds')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Username o password errati')
  })

  it('disables button while loading', async () => {
    const mockApi = api as any
    mockApi.post.mockReturnValue(new Promise(() => {}))

    const router = makeRouter()
    await router.push('/login')
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('#username').setValue('admin')
    await wrapper.find('#password').setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    const button = wrapper.find('button[type="submit"]')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('Accesso in corso')
  })

  it('redirects to home on successful login', async () => {
    const mockApi = api as any
    mockApi.post.mockResolvedValue({
      data: { access_token: 'tok', token_type: 'bearer' },
    })
    mockApi.get.mockResolvedValue({
      data: { id: 1, username: 'admin', created_at: '2024-01-01' },
    })

    const router = makeRouter()
    await router.push('/login')
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('#username').setValue('admin')
    await wrapper.find('#password').setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('home')
  })
})
