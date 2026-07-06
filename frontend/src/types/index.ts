export interface Family {
  id: number
  family_name: string
  address: string
  contact_number: string | null
  created_at: string
}

export interface Person {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  fingerprint_id: string | null
  family_id: number
  created_at: string
}

export interface Distribution {
  id: number
  family_id: number
  person_id: number
  package_type: string
  distribution_date: string
  notes: string | null
}

export interface FamilyDetail extends Family {
  members: Person[]
  distributions: Distribution[]
}

export interface PackageType {
  id: number
  name: string
  description: string | null
  cooldown_days: number
  is_active: boolean
}

export interface DistributionReceipt extends Distribution {
  is_emergency: boolean
  family_name: string
  person_name: string
}

export interface CooldownWarning {
  warning: string
  last_distribution_date: string
  cooldown_days: number
  next_allowed_date: string
}

export interface DistributionPage {
  items: DistributionReceipt[]
  total: number
  page: number
  page_size: number
}

export interface FamilyPage {
  items: Family[]
  total: number
  page: number
  page_size: number
}

export interface FamilySearchResult {
  id: number
  family_name: string
  address: string
  contact_number: string | null
  type: 'family'
}

export interface PersonSearchResult {
  id: number
  first_name: string
  last_name: string
  fingerprint_id: string | null
  family_id: number
  type: 'person'
}

export interface SearchResult {
  families: FamilySearchResult[]
  persons: PersonSearchResult[]
  total: number
  page: number
  page_size: number
}
