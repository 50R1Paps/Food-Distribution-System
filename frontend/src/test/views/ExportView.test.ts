import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api/dataTransfer', () => ({
  exportData: vi.fn(),
}))

import { exportData } from '@/api/dataTransfer'
import ExportView from '@/views/ExportView.vue'

describe('ExportView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders heading and export button', () => {
    const wrapper = mount(ExportView)
    expect(wrapper.find('h1').text()).toBe('Esporta Dati')
    expect(wrapper.find('button').text()).toContain('Scarica File JSON')
  })

  it('triggers export on button click', async () => {
    const blob = new Blob(['{"test":true}'], { type: 'application/json' })
    ;(exportData as any).mockResolvedValue(blob)

    const createObjectURL = vi.fn().mockReturnValue('blob:mock')
    const revokeObjectURL = vi.fn()
    Object.defineProperty(window.URL, 'createObjectURL', { value: createObjectURL, writable: true })
    Object.defineProperty(window.URL, 'revokeObjectURL', { value: revokeObjectURL, writable: true })

    const wrapper = mount(ExportView)
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(exportData).toHaveBeenCalledOnce()
    expect(createObjectURL).toHaveBeenCalledWith(blob)
    expect(wrapper.text()).toContain('Esportazione completata')
  })

  it('shows error on export failure', async () => {
    ;(exportData as any).mockRejectedValue({
      response: { data: { detail: 'Errore server' } },
    })

    const wrapper = mount(ExportView)
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Errore server')
  })

  it('disables button while loading', async () => {
    ;(exportData as any).mockReturnValue(new Promise(() => {}))

    const wrapper = mount(ExportView)
    await wrapper.find('button').trigger('click')
    await flushPromises()

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('Esportazione in corso')
  })
})
