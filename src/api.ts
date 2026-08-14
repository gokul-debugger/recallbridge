import type {
  MatchResponse,
  ProductInput,
  RecallCategory,
  RecallSearchResponse,
  RecallStats,
} from './types'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function fetchStats(): Promise<RecallStats> {
  return request('/api/stats')
}

export function searchRecalls(
  query = '',
  category: RecallCategory | '' = '',
): Promise<RecallSearchResponse> {
  const params = new URLSearchParams({ limit: '50' })
  if (query.trim()) params.set('q', query.trim())
  if (category) params.set('category', category)
  return request(`/api/recalls?${params}`)
}

export function matchProduct(product: ProductInput): Promise<MatchResponse> {
  const payload = {
    ...product,
    category: product.category || null,
  }
  return request('/api/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
