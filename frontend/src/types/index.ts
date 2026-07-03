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

export interface FamilyPage {
  items: Family[]
  total: number
  page: number
  page_size: number
}
