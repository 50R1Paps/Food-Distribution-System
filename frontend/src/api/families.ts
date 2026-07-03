import api from '@/api'
import type { Family, FamilyDetail, FamilyPage, Person } from '@/types'

export interface FamilyPayload {
  family_name: string
  address: string
  contact_number?: string | null
}

export interface MemberPayload {
  first_name: string
  last_name: string
  date_of_birth: string
  fingerprint_id?: string | null
}

export async function listFamilies(params: {
  search?: string
  page?: number
  page_size?: number
}): Promise<FamilyPage> {
  const { data } = await api.get('/families', { params })
  return data
}

export async function createFamily(payload: FamilyPayload): Promise<Family> {
  const { data } = await api.post('/families', payload)
  return data
}

export async function getFamily(id: number): Promise<FamilyDetail> {
  const { data } = await api.get(`/families/${id}`)
  return data
}

export async function updateFamily(
  id: number,
  payload: Partial<FamilyPayload>
): Promise<Family> {
  const { data } = await api.put(`/families/${id}`, payload)
  return data
}

export async function deleteFamily(id: number): Promise<void> {
  await api.delete(`/families/${id}`)
}

export async function addMember(
  familyId: number,
  payload: MemberPayload
): Promise<Person> {
  const { data } = await api.post(`/families/${familyId}/members`, payload)
  return data
}

export async function updateMember(
  id: number,
  payload: Partial<MemberPayload>
): Promise<Person> {
  const { data } = await api.put(`/members/${id}`, payload)
  return data
}

export async function deleteMember(id: number): Promise<void> {
  await api.delete(`/members/${id}`)
}
