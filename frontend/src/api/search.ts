import api from '@/api'
import type { SearchResult } from '@/types'

export async function search(
  q: string,
  params?: { page?: number; page_size?: number }
): Promise<SearchResult> {
  const { data } = await api.get('/search', {
    params: { q, ...params },
  })
  return data
}
