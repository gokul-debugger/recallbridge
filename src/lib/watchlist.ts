import type { ProductInput, WatchItem } from '../types'

const STORAGE_KEY = 'recallbridge.watchlist.v1'
const categories = new Set(['', 'consumer_product', 'food', 'medical_device'])

function isWatchItem(value: unknown): value is WatchItem {
  if (!value || typeof value !== 'object') return false
  const item = value as Record<string, unknown>
  const stringFields = ['id', 'created_at', 'product_name', 'brand', 'model', 'upc', 'lot']
  return stringFields.every((field) => typeof item[field] === 'string')
    && typeof item.category === 'string'
    && categories.has(item.category)
}

export function loadWatchlist(): WatchItem[] {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
    return Array.isArray(stored) ? stored.filter(isWatchItem) : []
  } catch {
    return []
  }
}

export function saveWatchlist(items: WatchItem[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  } catch {
    // The in-memory watchlist remains usable when browser storage is unavailable.
  }
}

export function createWatchItem(product: ProductInput): WatchItem {
  return {
    ...product,
    id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
  }
}
