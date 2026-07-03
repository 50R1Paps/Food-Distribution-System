import api from '@/api'
import type { DistributionPage, DistributionReceipt, PackageType } from '@/types'

export interface DistributionPayload {
  person_id?: number | null
  fingerprint_id?: string | null
  package_type_id: number
  notes?: string | null
  is_emergency?: boolean
}

export async function listPackageTypes(includeInactive = false): Promise<PackageType[]> {
  const { data } = await api.get('/package-types', {
    params: { include_inactive: includeInactive },
  })
  return data
}

export async function createDistribution(
  payload: DistributionPayload
): Promise<DistributionReceipt> {
  const { data } = await api.post('/distributions', payload)
  return data
}

export async function getDistribution(id: number): Promise<DistributionReceipt> {
  const { data } = await api.get(`/distributions/${id}`)
  return data
}

export async function listDistributions(params: {
  family_id?: number
  package_type?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}): Promise<DistributionPage> {
  const { data } = await api.get('/distributions', { params })
  return data
}
