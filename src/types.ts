export type RecallCategory = 'consumer_product' | 'food' | 'medical_device'
export type RecallSource = 'cpsc' | 'openfda_food' | 'openfda_device'

export interface ProductIdentifier {
  kind: string
  value: string
}

export interface RecallImage {
  url: string
  caption: string
}

export interface RecallRecord {
  id: string
  source: RecallSource
  source_id: string
  source_url: string
  title: string
  category: RecallCategory
  product_description: string
  hazard: string
  remedy: string
  recall_date: string
  status: string
  severity: string
  manufacturer: string
  affected_units: string
  identifiers: ProductIdentifier[]
  images: RecallImage[]
  synced_at: string
  is_demo: boolean
}

export interface RecallSearchResponse {
  items: RecallRecord[]
  total: number
  query: string
}

export interface SourceStat {
  source: RecallSource
  count: number
}

export interface RecallStats {
  total: number
  active: number
  latest_date: string | null
  demo_mode: boolean
  by_source: SourceStat[]
}

export interface ProductInput {
  product_name: string
  brand: string
  model: string
  upc: string
  lot: string
  category: RecallCategory | ''
}

export interface RecallMatch {
  recall: RecallRecord
  confidence: 'exact' | 'strong' | 'possible'
  score: number
  reasons: string[]
}

export interface MatchResponse {
  matches: RecallMatch[]
  checked: number
  exact_identifier_match: boolean
}

export interface WatchItem extends ProductInput {
  id: string
  created_at: string
}

export type AppView = 'browse' | 'match' | 'watchlist'
