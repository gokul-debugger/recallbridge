import { Bookmark, Search, Trash2 } from 'lucide-react'
import type { WatchItem } from '../types'

interface WatchlistViewProps {
  items: WatchItem[]
  onCheck: (item: WatchItem) => void
  onRemove: (id: string) => void
}

export function WatchlistView({ items, onCheck, onRemove }: WatchlistViewProps) {
  return (
    <section className="view" aria-labelledby="watchlist-title">
      <div className="view-heading">
        <div><span className="eyebrow">Stored in this browser</span><h1 id="watchlist-title">My watchlist</h1></div>
        <p>Saved product details remain on this device and are never added to the recall index.</p>
      </div>

      {items.length === 0 ? (
        <div className="watchlist-empty"><Bookmark size={30} /><h2>No saved products</h2><p>Open Check a product, enter an identifier, and save it for later checks.</p></div>
      ) : (
        <div className="watchlist-table">
          <div className="watchlist-table__header"><span>Product</span><span>Identifiers</span><span>Saved</span><span>Actions</span></div>
          {items.map((item) => (
            <div className="watchlist-item" key={item.id}>
              <span><strong>{item.product_name || item.model || item.upc}</strong><small>{item.brand || 'Brand not entered'}</small></span>
              <span><code>{item.model || item.upc || item.lot || 'Text only'}</code></span>
              <span>{new Date(item.created_at).toLocaleDateString()}</span>
              <span className="watch-actions"><button className="icon-text-button" onClick={() => onCheck(item)}><Search size={15} /> Check</button><button className="icon-button" aria-label={`Remove ${item.product_name || item.model || 'product'}`} onClick={() => onRemove(item.id)} title="Remove product"><Trash2 size={16} /></button></span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
