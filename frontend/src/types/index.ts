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

export interface ExportData {
  version: number
  exported_at: string
  package_types: ExportPackageType[]
  families: ExportFamily[]
  persons: ExportPerson[]
  distributions: ExportDistribution[]
}

export interface ExportPackageType {
  id: number
  name: string
  description: string | null
  cooldown_days: number
  is_active: boolean
}

export interface ExportFamily {
  id: number
  family_name: string
  address: string
  contact_number: string | null
  created_at: string
}

export interface ExportPerson {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  fingerprint_id: string | null
  family_id: number
  created_at: string
}

export interface ExportDistribution {
  id: number
  family_id: number
  person_id: number
  package_type: string
  distribution_date: string
  notes: string | null
  is_emergency: boolean
}

export interface ImportSummaryEntry {
  new: number
  existing: number
}

export interface ImportConflict {
  entity: string
  identifier: string
  message: string
}

export interface ImportPreview {
  dry_run: boolean
  mode: string
  summary: Record<string, ImportSummaryEntry>
  conflicts: ImportConflict[]
}

// --- Stats & Reports ---

export interface OverviewStats {
  total_families: number
  total_persons: number
  total_distributions: number
  distributions_this_month: number
}

export interface PackageTypeStat {
  package_type: string
  count: number
}

export interface DistributionStats {
  total: number
  by_package_type: PackageTypeStat[]
}

export interface FamilyCoverageStats {
  total_families: number
  families_served: number
  families_not_served: number
}

export interface TrendPoint {
  period: string
  count: number
}

export interface TrendsStats {
  granularity: string
  points: TrendPoint[]
}
