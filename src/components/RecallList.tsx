import { ChevronRight } from 'lucide-react'
import type { RecallRecord } from '../types'

const categoryNames = {
  consumer_product: 'Consumer product',
  food: 'Food',
  medical_device: 'Medical device',
}

interface RecallListProps {
  items: RecallRecord[]
  selectedId: string | null
  loading: boolean
  onSelect: (recall: RecallRecord) => void
}

export function RecallList({ items, selectedId, loading, onSelect }: RecallListProps) {
  if (loading) return <div className="list-state">Loading recall records…</div>
  if (items.length === 0) return <div className="list-state">No recalls matched those filters.</div>

  return (
    <div className="recall-list" aria-label="Recall search results">
      {items.map((recall) => (
        <button
          key={recall.id}
          className={selectedId === recall.id ? 'recall-row recall-row--selected' : 'recall-row'}
          aria-pressed={selectedId === recall.id}
          onClick={() => onSelect(recall)}
        >
          <span className={`category-indicator category-indicator--${recall.category}`} />
          <span className="recall-row__body">
            <span className="recall-row__meta">{categoryNames[recall.category]} · {recall.recall_date}</span>
            <strong>{recall.title}</strong>
            <small>{recall.manufacturer || recall.severity}</small>
          </span>
          <ChevronRight size={17} />
        </button>
      ))}
    </div>
  )
}
