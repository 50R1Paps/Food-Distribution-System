import api from '@/api'
import type {
  OverviewStats,
  DistributionStats,
  FamilyCoverageStats,
  TrendsStats,
} from '@/types'

export async function getOverview(): Promise<OverviewStats> {
  const { data } = await api.get('/stats/overview')
  return data
}

export async function getDistributionStats(params?: {
  date_from?: string
  date_to?: string
}): Promise<DistributionStats> {
  const { data } = await api.get('/stats/distributions', { params })
  return data
}

export async function getFamilyCoverage(): Promise<FamilyCoverageStats> {
  const { data } = await api.get('/stats/families')
  return data
}

export async function getTrends(params?: {
  granularity?: 'monthly' | 'weekly'
}): Promise<TrendsStats> {
  const { data } = await api.get('/stats/trends', { params })
  return data
}

export async function downloadDistributionsReport(params?: {
  date_from?: string
  date_to?: string
}): Promise<Blob> {
  const response = await api.get('/reports/distributions', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function downloadFamiliesReport(): Promise<Blob> {
  const response = await api.get('/reports/families', {
    responseType: 'blob',
  })
  return response.data
}
