import api from '@/api'
import type { ImportPreview } from '@/types'

export async function exportData(): Promise<Blob> {
  const response = await api.get('/export', { responseType: 'blob' })
  return response.data
}

export async function importData(
  payload: Record<string, unknown>,
  params: { dry_run?: boolean; mode?: 'merge' | 'replace' }
): Promise<ImportPreview> {
  const { data } = await api.post('/import', payload, {
    params: {
      dry_run: params.dry_run ?? true,
      mode: params.mode ?? 'merge',
    },
  })
  return data
}
