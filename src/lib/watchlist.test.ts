import { beforeEach, describe, expect, it } from 'vitest'
import { createWatchItem, loadWatchlist, saveWatchlist } from './watchlist'

const product = {
  product_name: 'QuickHeat toaster',
  brand: 'Northstar',
  model: 'QH-220',
  upc: '',
  lot: '',
  category: 'consumer_product' as const,
}

describe('watchlist storage', () => {
  beforeEach(() => localStorage.clear())

  it('creates and restores a local watch item', () => {
    const item = createWatchItem(product)
    saveWatchlist([item])

    expect(loadWatchlist()).toEqual([item])
    expect(item.id).toBe('00000000-0000-4000-8000-000000000001')
  })

  it('recovers from invalid browser storage', () => {
    localStorage.setItem('recallbridge.watchlist.v1', '{broken')

    expect(loadWatchlist()).toEqual([])
  })

  it('drops malformed entries from browser storage', () => {
    localStorage.setItem('recallbridge.watchlist.v1', JSON.stringify([{ id: 'incomplete' }]))

    expect(loadWatchlist()).toEqual([])
  })
})
